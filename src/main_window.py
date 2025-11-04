from PyQt6.QtCore import QItemSelectionRange, Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QShortcut, QKeySequence
from PyQt6.QtWidgets import (
	QMainWindow, QGraphicsScene,
	QFileDialog, QListView, QDockWidget, QLineEdit
)
from PyQt6.uic import loadUi
from PyQt6Ads import CDockManager

import PyQt6Ads as ads

from src.directory_tag_model import DirectoryTagModel
from src.float_dock_widget import FloatDockWidget
from src.graphics_view import GraphicsView
from src.image_tag_model import ImageTagModel
from src.image import Image
from src.directory import Directory
from src.directory_image_model import DirectoryImageModel
from src.panels.image_selector import ImageSelector
from src.panels.image_viewer import ImageViewer
from src.panels.tag_editor import TagEditor
from src.panels.tag_viewer import TagViewer


class MainWindow(QMainWindow):
	image_loaded = pyqtSignal(Image)

	def __init__(self):
		super().__init__()

		# Instance variables
		self.tag_editor_list_view = None
		self.directory_image_model = DirectoryImageModel()
		self.directory_tag_model = DirectoryTagModel()

		# Assemble interface

		image_viewer = ImageViewer()
		tag_viewer = TagViewer()
		tag_editor = TagEditor()
		image_selector = ImageSelector()

		CDockManager.setConfigFlags(CDockManager.configFlags().DefaultOpaqueConfig)
		CDockManager.setConfigFlag(CDockManager.configFlags().ActiveTabHasCloseButton, False)

		dock_manager = CDockManager(self)

		self.tag_viewer_dock = dock_manager.createDockWidget("Tag Viewer")
		self.tag_viewer_dock.setWidget(tag_viewer)
		dock_manager.addDockWidget(ads.DockWidgetArea.LeftDockWidgetArea, self.tag_viewer_dock)

		self.tag_editor_dock = dock_manager.createDockWidget("Tag Editor")
		self.tag_editor_dock.setWidget(tag_editor)
		dock_manager.addDockWidget(ads.DockWidgetArea.LeftDockWidgetArea, self.tag_editor_dock)

		self.image_viewer_dock = dock_manager.createDockWidget("Image Viewer")
		self.image_viewer_dock.setWidget(image_viewer)
		dock_manager.addDockWidget(ads.DockWidgetArea.LeftDockWidgetArea, self.image_viewer_dock)

		self.image_selector_dock = dock_manager.createDockWidget("Image Selector")
		self.image_selector_dock.setWidget(image_selector)
		dock_manager.addDockWidget(ads.DockWidgetArea.LeftDockWidgetArea, self.image_selector_dock)

		self.setWindowTitle("descryptor")

		self.image_viewer_gfx_view: GraphicsView = image_viewer.gfx_view
		self.selector_list_view: QListView = image_selector.listview
		self.tag_editor_list_view: QListView = tag_editor.list_view
		self.tag_viewer_list_view: QListView = tag_viewer.listview
		self.tag_editor_line_edit: QLineEdit = tag_editor.line_edit

		# Set up selector list view model
		self.selector_list_view.setModel(self.directory_image_model)

		# Set up image tags list view model
		self.image_tag_model = ImageTagModel()
		self.tag_editor_list_view.setModel(self.image_tag_model)

		# Set up directory tags list view model
		self.tag_viewer_list_view.setModel(self.directory_tag_model)

		# Set up graphics view
		self.scene = QGraphicsScene()
		self.image_viewer_gfx_view.setScene(self.scene)
		self.image_viewer_gfx_view.setRenderHint(QPainter.RenderHint.Antialiasing)

		# Create keyboard shortcuts

		# self.actionOpen.setShortcut(QKeySequence.StandardKey.Open)
		# self.actionQuit.setShortcut(QKeySequence.StandardKey.Quit)
		# self.actionSave.setShortcut(QKeySequence.StandardKey.Save)
		# self.delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self.tag_editor_list_view)
		# self.next_image_shortcut = QShortcut(QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_N), self)
		# self.prev_image_shortcut = QShortcut(QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_P), self)

		# Connect signals

		# self.actionOpen.triggered.connect(self.open_directory)
		# self.actionQuit.triggered.connect(self.close)
		# self.actionSave.triggered.connect(self.save)
		# self.delete_shortcut.activated.connect(self.delete_selected_item)
		# self.next_image_shortcut.activated.connect(self.select_next_image)
		# self.prev_image_shortcut.activated.connect(self.select_prev_image)
		self.image_loaded.connect(self.directory_tag_model.on_image_loaded)
		self.selector_list_view.selectionModel().selectionChanged.connect(self.display_image)
		self.image_tag_model.image_tags_modified.connect(self.directory_image_model.on_image_tags_modified)
		self.image_tag_model.image_tags_modified.connect(self.directory_tag_model.on_image_tags_modified)
		self.tag_editor_line_edit.returnPressed.connect(self.add_tag)

		self.tag_editor_line_edit.setEnabled(False) # enabled once something is loaded

		# Auto load image directory for testing
		self.open_directory()

	def add_tag(self):
		editor = self.tag_editor_line_edit
		text = editor.text().strip()
		if not text:
			return

		indexes = self.tag_editor_list_view.selectedIndexes()
		if len(indexes) > 0:
			index = indexes[0]
			self.image_tag_model.insert_tag(text, index.row())
			self.tag_editor_list_view.setCurrentIndex(index)
		else:
			self.image_tag_model.append_tag(text)

		editor.clear()
		self.update_dynamic_labels(image=self.image_tag_model.image)

	def reset_views(self):
		"""Clears viewer, tag editor, etc. after loading a directory, for example."""
		model: ImageTagModel | None = self.tag_editor_list_view.model()
		if model is not None:
			model.clear()

	def delete_selected_item(self):
		indexes = self.tag_editor_list_view.selectedIndexes()
		if indexes:
			index = indexes[0]
			row = index.row()
			self.image_tag_model.remove_tag_at(row)

		self.update_dynamic_labels(image=self.image_tag_model.image)

	def display_image(self, selected_items: QItemSelectionRange, deselected_items):
		"""Display selected image in graphics view"""

		if not selected_items:
			return

		index = selected_items.indexes()[0]  # Take the first selected item

		image: Image = self.directory_image_model.data(index, Qt.ItemDataRole.UserRole)

		self.image_tag_model.set_image(image)
		self.image_viewer_gfx_view.load_image(image)
		self.image_loaded.emit(image)
		self.update_dynamic_labels(image=image)

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
		self.tag_editor_line_edit.setEnabled(True)

		self.reset_views()
		self.update_dynamic_labels(directory=directory)

	def save(self):
		self.directory_image_model.save()

	def select_next_image(self):
		view = self.selector_list_view
		model = view.model()
		current_index = view.currentIndex()
		if current_index.isValid() and current_index.row() < model.rowCount() - 1:
			next_index = model.index(current_index.row() + 1, 0)
			view.setCurrentIndex(next_index)

	def select_prev_image(self):
		view = self.selector_list_view
		model = view.model()
		current_index = view.currentIndex()
		if current_index.isValid() and current_index.row() > 0:
			prev_index = model.index(current_index.row() - 1, 0)
			view.setCurrentIndex(prev_index)

	def update_dynamic_labels(self, directory: Directory | None = None, image: Image | None = None):

		if image:
			self.image_viewer_dock.setWindowTitle(image.path.name)
			self.tag_editor_dock.setWindowTitle("Image Tags ({})".format(len(image.tags)))
		else:
			self.image_viewer_dock.setWindowTitle("Viewer")
			self.tag_editor_dock.setWindowTitle("Image Tags")
			self.selector_list_view.selectionModel().clear()
			self.image_viewer_gfx_view.scene().clear()
			self.tag_editor_line_edit.clear()

		if directory:
			window_title = f"descryptor — {str(directory.path)}"
			self.setWindowTitle(window_title)

		self.tag_viewer_dock.setWindowTitle("Directory Tags ({})".format(len(self.directory_tag_model.tag_map)))