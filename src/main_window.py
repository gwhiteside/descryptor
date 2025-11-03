from PyQt6.QtCore import QItemSelectionRange, Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QShortcut, QKeySequence
from PyQt6.QtWidgets import (
	QMainWindow, QGraphicsScene,
	QFileDialog, QMessageBox, QListView, QDockWidget, QLineEdit
)
from PyQt6.uic import loadUi

from src.directory_tag_model import DirectoryTagModel
from src.float_dock_widget import FloatDockWidget
from src.graphics_view import GraphicsView
from src.image_tag_model import ImageTagModel
from src.image import Image
from src.directory import Directory
from src.directory_image_model import DirectoryImageModel


class MainWindow(QMainWindow):
	image_loaded = pyqtSignal(Image)

	def __init__(self):
		super().__init__()

		# Instance variables
		self.directory_image_model = DirectoryImageModel()
		self.directory_tag_model = DirectoryTagModel()

		# Load interface
		loadUi('src/main_window.ui', self)
		self.viewerDockWidget: FloatDockWidget = loadUi("src/viewer_dock_widget.ui")
		self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.viewerDockWidget)

		# Small workaround to get dock widgets to use all space. Central widget must be set after
		# dock widgets are added, but loadUi sets the central widget first. So do it again here.
		self.cw = self.centralWidget()
		self.setCentralWidget(None)
		self.setCentralWidget(self.cw)

		#self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.viewerDockWidget)

		# Set some explicit references to make the IDE experience more pleasant
		self.viewerGraphicsView: GraphicsView = self.findChild(GraphicsView, "viewerGraphicsView")
		self.selectorListView: QListView = self.findChild(QListView, "selectorListView")
		self.selectorDockWidget: QDockWidget = self.findChild(QDockWidget, "selectorDockWidget")
		#self.viewerDockWidget: FloatDockWidget = self.findChild(FloatDockWidget, "viewerDockWidget")
		self.imgtagsDockWidget: QDockWidget = self.findChild(QDockWidget, "imgtagsDockWidget")
		self.dirtagsDockWidget: QDockWidget = self.findChild(QDockWidget, "dirtagsDockWidget")
		self.imgtagListView: QListView = self.findChild(QListView, "imgtagListView")
		self.dirtagListView: QListView = self.findChild(QListView, "dirtagListView")
		self.imgtagLineEdit: QLineEdit = self.findChild(QLineEdit, "imgtagLineEdit")

		# Set up dock widgets
		self.splitDockWidget(self.selectorDockWidget, self.viewerDockWidget, Qt.Orientation.Horizontal)
		self.splitDockWidget(self.viewerDockWidget, self.imgtagsDockWidget, Qt.Orientation.Horizontal)
		self.splitDockWidget(self.imgtagsDockWidget, self.dirtagsDockWidget, Qt.Orientation.Horizontal)

		# Set up selector list view model
		#self.selectorListViewModel = QStandardItemModel()
		self.selectorListView.setModel(self.directory_image_model)
		self.selectorListView.setIconSize(QSize(128, 128))
		self.selectorListView.setGridSize(QSize(150,150))
		self.selectorListView.setSpacing(8)
		self.selectorListView.setViewMode(QListView.ViewMode.IconMode)
		self.selectorListView.setResizeMode(QListView.ResizeMode.Adjust)
		self.selectorListView.setUniformItemSizes(True)

		# Set up image tags list view model
		self.image_tag_model = ImageTagModel()
		self.imgtagListView.setModel(self.image_tag_model)
		#self.imgtagListView.setItemDelegate(StyledItemDelegate())

		# Set up directory tags list view model
		#self.dirtagsListViewModel = QStringListModel()
		self.dirtagListView.setModel(self.directory_tag_model)

		# Set up graphics view
		self.scene = QGraphicsScene()
		self.viewerGraphicsView.setScene(self.scene)
		self.viewerGraphicsView.setRenderHint(QPainter.RenderHint.Antialiasing)

		# Create keyboard shortcuts

		self.actionOpen.setShortcut(QKeySequence.StandardKey.Open)
		self.actionQuit.setShortcut(QKeySequence.StandardKey.Quit)
		self.actionSave.setShortcut(QKeySequence.StandardKey.Save)
		self.delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self.imgtagListView)
		self.next_image_shortcut = QShortcut(QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_N), self)
		self.prev_image_shortcut = QShortcut(QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_P), self)

		# Connect signals
		self.actionOpen.triggered.connect(self.open_directory)
		self.actionQuit.triggered.connect(self.close)
		self.actionSave.triggered.connect(self.save)
		self.delete_shortcut.activated.connect(self.delete_selected_item)
		self.next_image_shortcut.activated.connect(self.select_next_image)
		self.prev_image_shortcut.activated.connect(self.select_prev_image)
		self.image_loaded.connect(self.directory_tag_model.on_image_loaded)
		self.selectorListView.selectionModel().selectionChanged.connect(self.display_image)
		self.image_tag_model.image_tags_modified.connect(self.directory_image_model.on_image_tags_modified)
		self.image_tag_model.image_tags_modified.connect(self.directory_tag_model.on_image_tags_modified)
		self.imgtagLineEdit.returnPressed.connect(self.add_tag)

		self.imgtagLineEdit.setEnabled(False) # enabled once something is loaded

		# Auto load image directory for testing
		self.open_directory()

	def add_tag(self):
		editor = self.imgtagLineEdit
		text = editor.text().strip()
		if not text:
			return

		indexes = self.imgtagListView.selectedIndexes()
		if len(indexes) > 0:
			index = indexes[0]
			self.image_tag_model.insert_tag(text, index.row())
			self.imgtagListView.setCurrentIndex(index)
		else:
			self.image_tag_model.append_tag(text)

		editor.clear()

	def delete_selected_item(self):
		indexes = self.imgtagListView.selectedIndexes()
		if indexes:
			index = indexes[0]
			row = index.row()
			self.image_tag_model.remove_tag_at(row)

		# TODO selector and directory tags need to be informed of updates

	def display_image(self, selected_items: QItemSelectionRange, deselected_items):
		"""Display selected image in graphics view"""

		if not selected_items:
			return

		index = selected_items.indexes()[0]  # Take the first selected item

		image: Image = self.directory_image_model.data(index, Qt.ItemDataRole.UserRole)

		self.image_tag_model.set_image(image)
		self.imgtagsDockWidget.setWindowTitle("Image Tags ({})".format(len(image.tags)))
		self.viewerGraphicsView.load_image(image)

		self.image_loaded.emit(image)

	def open_directory(self):
		"""Open directory dialog and load images"""

		path = QFileDialog.getExistingDirectory(
			self,
			"Select Directory",
			"",
			QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
		)

		if not path:
			# TODO display error message
			return

		directory = Directory(path)

		#try:
		self.directory_image_model.setDirectory(directory)
		self.directory_tag_model.load(directory)
		self.imgtagLineEdit.setEnabled(True)
		#except Exception as e:
		#	QMessageBox.critical(self, "Error", f"Failed to load directory: {str(e)}")

	def save(self):
		self.directory_image_model.save()

	def select_next_image(self):
		view = self.selectorListView
		model = view.model()
		current_index = view.currentIndex()
		if current_index.isValid() and current_index.row() < model.rowCount() - 1:
			next_index = model.index(current_index.row() + 1, 0)
			view.setCurrentIndex(next_index)

	def select_prev_image(self):
		view = self.selectorListView
		model = view.model()
		current_index = view.currentIndex()
		if current_index.isValid() and current_index.row() > 0:
			prev_index = model.index(current_index.row() - 1, 0)
			view.setCurrentIndex(prev_index)
