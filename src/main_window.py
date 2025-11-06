from PyQt6.QtCore import QItemSelectionRange, Qt, QSize, pyqtSignal, QRect
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QShortcut
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QDockWidget, QMenu, QHBoxLayout, QWidget

from src.directory_tag_model import DirectoryTagModel
from src.float_dock_widget import FloatDockWidget
from src.image_tag_model import ImageTagModel
from src.image import Image
from src.directory import Directory
from src.directory_image_model import DirectoryImageModel
from src.main_menu import setup_menu
from src.panels.image_selector import ImageSelector
from src.panels.image_viewer import ImageViewer
from src.panels.tag_editor import TagEditor
from src.panels.tag_viewer import TagIndex


class MainWindow(QMainWindow):
	image_loaded = pyqtSignal(Image)

	def __init__(self):
		super().__init__()

		self.current_image: Image | None = None
		self.current_directory: Directory | None = None

		# Assemble interface

		self.setWindowTitle("descryptor")

		self.setDockOptions(
			QMainWindow.DockOption.AllowNestedDocks |
			QMainWindow.DockOption.AllowTabbedDocks |
			QMainWindow.DockOption.AnimatedDocks
		)

		self.image_viewer = ImageViewer()
		self.image_selector = ImageSelector()
		self.tag_editor = TagEditor()
		self.tag_index = TagIndex()

		self.image_selector_dock = QDockWidget("Image Selector")
		self.image_selector_dock.setWidget(self.image_selector)
		self.image_viewer_dock = FloatDockWidget("Image Viewer")
		self.image_viewer_dock.setWidget(self.image_viewer)
		self.tag_editor_dock = FloatDockWidget("Tag Editor")
		self.tag_editor_dock.setWidget(self.tag_editor)
		self.tag_index_dock = FloatDockWidget("Tag Index")
		self.tag_index_dock.setWidget(self.tag_index)
		self.unified_tag_dock = QDockWidget("Tags")

		self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.image_selector_dock)
		self.splitDockWidget(self.image_selector_dock, self.image_viewer_dock, Qt.Orientation.Horizontal)
		self.splitDockWidget(self.image_viewer_dock, self.tag_editor_dock, Qt.Orientation.Horizontal)
		self.splitDockWidget(self.tag_editor_dock, self.tag_index_dock, Qt.Orientation.Horizontal)

		self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.unified_tag_dock)
		self.unified_tag_dock.hide()

		self.setCentralWidget(None)
		self.resizeDocks(
			[
				self.image_selector_dock,
				self.image_viewer_dock,
				self.tag_editor_dock,
				self.tag_index_dock
			],
			[2, 2, 1, 1],
			Qt.Orientation.Horizontal
		)

		self.resize(QSize(1280, 768))

		# Create menu bar

		setup_menu(self)

		# Set models

		self.directory_image_model = DirectoryImageModel()
		self.directory_tag_model = DirectoryTagModel()
		self.image_tag_model = ImageTagModel()

		self.image_selector.listview.setModel(self.directory_image_model)
		self.tag_editor.list_view.setModel(self.image_tag_model)
		self.tag_index.listview.setModel(self.directory_tag_model)

		# Create interface shortcuts

		delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self.tag_editor.list_view)
		next_image_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_N), self)
		prev_image_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_P), self)

		# Connect signals

		delete_shortcut.activated.connect(self.delete_selected_item)
		next_image_shortcut.activated.connect(self.select_next_image)
		prev_image_shortcut.activated.connect(self.select_prev_image)
		self.image_loaded.connect(self.directory_tag_model.on_image_loaded)
		self.image_selector.listview.selectionModel().selectionChanged.connect(self.display_image)
		self.image_tag_model.image_tags_modified.connect(self.directory_image_model.on_image_tags_modified)
		self.image_tag_model.image_tags_modified.connect(self.directory_tag_model.on_image_tags_modified)
		self.tag_editor.line_edit.returnPressed.connect(self.add_tag)

		# Set initial state for widgets, etc.

		self.tag_editor.line_edit.setEnabled(False) # enabled once something is loaded
		self.recent_menu.setEnabled(False) # enabled when there are previously opened locations

		# Auto load image directory for testing
		self.open_directory()

	def add_tag(self):
		editor = self.tag_editor.line_edit
		text = editor.text().strip()
		if not text:
			return

		indexes = self.tag_editor.list_view.selectedIndexes()
		if len(indexes) > 0:
			index = indexes[0]
			self.image_tag_model.insert_tag(text, index.row())
			self.tag_editor.list_view.setCurrentIndex(index)
		else:
			self.image_tag_model.append_tag(text)

		editor.clear()
		self.update_dynamic_labels()

	def reset_views(self):
		"""Clears viewer, tag editor, etc. after loading a directory, for example."""
		model: ImageTagModel | None = self.tag_editor.list_view.model()
		if model is not None:
			model.clear()

		self.current_image = None

	def delete_selected_item(self):
		indexes = self.tag_editor.list_view.selectedIndexes()
		if indexes:
			index = indexes[0]
			row = index.row()
			self.image_tag_model.remove_tag_at(row)

		self.update_dynamic_labels()

	def display_image(self, selected_items: QItemSelectionRange, deselected_items):
		"""Display selected image in graphics view"""

		if not selected_items:
			return

		index = selected_items.indexes()[0]  # Take the first selected item

		image: Image = self.directory_image_model.data(index, Qt.ItemDataRole.UserRole)

		self.image_tag_model.set_image(image)
		self.image_viewer.gfx_view.load_image(image)
		self.image_loaded.emit(image)
		self.current_image = image
		self.update_dynamic_labels()

	def open_directory(self):
		"""Open directory dialog and load images"""

		path = QFileDialog.getExistingDirectory(
			self,
			"Select Directory",
			"",
			QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
		)

		if not path:
			return

		directory = Directory(path)

		self.directory_image_model.setDirectory(directory)
		self.directory_tag_model.load(directory)
		self.tag_editor.line_edit.setEnabled(True)

		self.reset_views()
		self.current_directory = directory
		self.update_dynamic_labels()

	def save(self):
		self.directory_image_model.save()

	def select_next_image(self):
		view = self.image_selector.listview
		model = view.model()
		current_index = view.currentIndex()
		if current_index.isValid() and current_index.row() < model.rowCount() - 1:
			next_index = model.index(current_index.row() + 1, 0)
			view.setCurrentIndex(next_index)

	def select_prev_image(self):
		view = self.image_selector.listview
		model = view.model()
		current_index = view.currentIndex()
		if current_index.isValid() and current_index.row() > 0:
			prev_index = model.index(current_index.row() - 1, 0)
			view.setCurrentIndex(prev_index)

	def toggle_unified_dock(self, unified: bool):
		if unified:
			selector_width = self.image_selector.width()
			viewer_width = self.image_viewer.width()
			editor_width = self.tag_editor.width()
			index_width = self.tag_index.width()

			self.tag_editor_dock.hide()
			self.tag_index_dock.hide()

			layout = QHBoxLayout()
			layout.setContentsMargins(0, 0, 0, 0)
			layout.setSpacing(0)
			layout.addWidget(self.tag_editor, 1)
			layout.addWidget(self.tag_index, 1)

			widget = QWidget()
			widget.setLayout(layout)

			self.unified_tag_dock.setWidget(widget)

			self.resizeDocks(
				[self.image_selector_dock, self.image_viewer_dock, self.unified_tag_dock],
				[selector_width, viewer_width, editor_width + index_width],
				Qt.Orientation.Horizontal
			)

			self.unified_tag_dock.show()
		else:
			self.unified_tag_dock.hide()
			self.tag_editor_dock.setWidget(self.tag_editor)
			self.tag_index_dock.setWidget(self.tag_index)
			self.tag_editor_dock.show()
			self.tag_index_dock.show()

	def update_dynamic_labels(self):
		if self.current_image:
			image_viewer_title = self.current_image.path.name
			tag_editor_title = "Image Tags ({})".format(len(self.current_image.tags))
			unified_tag_title = "Tags ({}/{})".format(len(self.current_image.tags), len(self.directory_tag_model.tag_map))
		else:
			image_viewer_title = "Viewer"
			tag_editor_title = "Image Tags"
			unified_tag_title = "Tags"
			self.image_selector.listview.selectionModel().clear()
			self.image_viewer.gfx_view.scene().clear()
			self.tag_editor.line_edit.clear()

		if self.current_directory:
			window_title = f"descryptor — {str(self.current_directory.path)}"
		else:
			window_title = "descryptor"

		self.setWindowTitle(window_title)
		self.image_viewer_dock.setWindowTitle(image_viewer_title)
		self.tag_editor_dock.setWindowTitle(tag_editor_title)
		self.unified_tag_dock.setWindowTitle(unified_tag_title)

		self.tag_index_dock.setWindowTitle("Directory Tags ({})".format(len(self.directory_tag_model.tag_map)))