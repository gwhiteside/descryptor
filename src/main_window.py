from PyQt6.QtCore import QItemSelectionRange, Qt, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QShortcut, QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QDockWidget, QHBoxLayout, QWidget

from src.config import Config, Setting
from src.directory import Directory
from src.directory_image_model import DirectoryImageModel
from src.directory_tag_model import DirectoryTagModel
from src.image import Image
from src.image_tag_model import ImageTagModel
from src.main_menu import setup_menu
from src.panels.image_selector import ImageSelector
from src.panels.image_viewer import ImageViewer
from src.panels.tag_editor import TagEditor
from src.panels.tag_index import TagIndex
from src.panels.unified_tagger import UnifiedTagger
from src.shortcut_manager import ShortcutManager
from src.shortcuts import SHORTCUTS


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

		self.image_selector = ImageSelector("Image Selector")
		self.image_viewer = ImageViewer("Image Viewer")
		self.tag_editor = TagEditor("Tag Editor")
		self.tag_index = TagIndex("Tag Index")
		self.unified_tagger = UnifiedTagger("Tags")

		self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.image_selector)
		self.splitDockWidget(self.image_selector, self.image_viewer, Qt.Orientation.Horizontal)
		self.splitDockWidget(self.image_viewer, self.tag_editor, Qt.Orientation.Horizontal)
		self.splitDockWidget(self.tag_editor, self.tag_index, Qt.Orientation.Horizontal)

		self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.unified_tagger)
		self.unified_tagger.hide()

		self.setCentralWidget(None)
		self.resizeDocks(
			[
				self.image_selector,
				self.image_viewer,
				self.tag_editor,
				self.tag_index
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
		self.tag_editor.set_model(self.image_tag_model)
		self.tag_index.set_model(self.directory_tag_model)
		self.unified_tagger.set_models(self.image_tag_model, self.directory_tag_model)

		# Create interface shortcuts

		shortcut = ShortcutManager.instance()
		shortcut.create("next_image", self, self.select_next_image)
		shortcut.create("previous_image", self, self.select_prev_image)

		# Connect signals

		self.image_loaded.connect(self.directory_tag_model.on_image_loaded)
		self.image_selector.listview.selectionModel().selectionChanged.connect(self.display_image)
		self.image_tag_model.image_tags_modified.connect(self.directory_image_model.on_image_tags_modified)
		self.image_tag_model.image_tags_modified.connect(self.directory_tag_model.on_image_tags_modified)
		self.tag_editor.data_changed.connect(self.update_dynamic_labels)
		self.tag_index.data_changed.connect(self.update_dynamic_labels)
		self.unified_tagger.data_changed.connect(self.update_dynamic_labels)

		# Restore window geometry and state

		if Config.read(Setting.RestoreLayout):
			self.restoreGeometry(Config.read(Setting.LayoutGeometry))
			self.restoreState(Config.read(Setting.LayoutState))
			self.unified_dock_action.setChecked(Config.read(Setting.UnifiedTagDock))

	def reset_views(self):
		"""Clears viewer, tag editor, etc. after loading a directory, for example."""
		self.tag_editor.clear_model()

		self.current_image = None

	def display_image(self, selected_items: QItemSelectionRange, deselected_items: QItemSelectionRange):
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

	def on_open_recent(self):
		action: QAction = self.sender()
		if action:
			path = action.data()
			self.open_directory(path)

	def open_directory(self, path: str | None = None):
		"""Open directory dialog and load images"""

		if not path:
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

		self.recent_menu.add_entry(path)

		self.reset_views()
		self.current_directory = directory
		self.update_dynamic_labels()

	def save_tags(self):
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

			self.tag_editor.hide()
			self.tag_index.hide()

			self.resizeDocks(
				[self.image_selector, self.image_viewer, self.unified_tagger],
				[selector_width, viewer_width, editor_width + index_width],
				Qt.Orientation.Horizontal
			)

			self.unified_tagger.show()
		else:
			self.unified_tagger.hide()
			self.tag_editor.show()
			self.tag_index.show()

	def update_dynamic_labels(self):
		if self.current_image:
			image_viewer_title = self.current_image.path.name
			tag_editor_title = "Image Tags ({})".format(len(self.current_image.tags))
			unified_tag_title = "Tags ({}/{})".format(len(self.current_image.tags), len(self.directory_tag_model.tag_map))
			self.tag_editor.set_input_enabled(True)
			self.unified_tagger.set_input_enabled(True)
		else:
			image_viewer_title = "Viewer"
			tag_editor_title = "Image Tags"
			unified_tag_title = "Tags"
			self.image_selector.listview.selectionModel().clear()
			self.image_viewer.gfx_view.scene().clear()
			self.tag_editor.clear_input()
			self.tag_editor.set_input_enabled(False)
			self.unified_tagger.set_input_enabled(False)

		if self.current_directory:
			window_title = str(self.current_directory.path)
		else:
			window_title = None

		self.setWindowTitle(window_title)
		self.image_viewer.setWindowTitle(image_viewer_title)
		self.tag_editor.setWindowTitle(tag_editor_title)
		self.unified_tagger.setWindowTitle(unified_tag_title)

		self.tag_index.setWindowTitle("Directory Tags ({})".format(len(self.directory_tag_model.tag_map)))

	def closeEvent(self, event: QCloseEvent | None):
		if Config.read(Setting.RestoreLayout):
			Config.write(Setting.LayoutGeometry, self.saveGeometry())
			Config.write(Setting.LayoutState, self.saveState())
			Config.write(Setting.UnifiedTagDock, self.unified_dock_action.isChecked())

		ShortcutManager.instance().save_shortcuts()