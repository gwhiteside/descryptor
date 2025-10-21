from pathlib import Path

from PyQt6.QtCore import QItemSelectionRange, Qt, QStringListModel, QSize
from PyQt6.QtGui import QPixmap, QPainter, QIcon, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
	QMainWindow, QGraphicsScene,
	QFileDialog, QMessageBox, QListView, QGraphicsView, QDockWidget
)
from PyQt6.uic import loadUi

from src.float_dock_widget import FloatDockWidget
from src.graphics_view import GraphicsView
from src.styled_item_delegate import StyledItemDelegate
from src.tag_image import TagImage


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		# Instance variables
		self.current_image_path = None
		self.directory_tags_set: set = set()

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

		# Set up dock widgets
		self.splitDockWidget(self.selectorDockWidget, self.viewerDockWidget, Qt.Orientation.Horizontal)
		self.splitDockWidget(self.viewerDockWidget, self.imgtagsDockWidget, Qt.Orientation.Horizontal)
		self.splitDockWidget(self.imgtagsDockWidget, self.dirtagsDockWidget, Qt.Orientation.Horizontal)

		# Set up selector list view model
		self.selectorListViewModel = QStandardItemModel()
		self.selectorListView.setModel(self.selectorListViewModel)
		self.selectorListView.setIconSize(QSize(128, 128))
		self.selectorListView.setViewMode(QListView.ViewMode.IconMode)
		self.selectorListView.setResizeMode(QListView.ResizeMode.Adjust)
		self.selectorListView.setUniformItemSizes(True)

		# Set up image tags list view model
		self.imgtagListViewModel = QStringListModel()
		self.imgtagListView.setModel(self.imgtagListViewModel)
		self.imgtagListView.setItemDelegate(StyledItemDelegate())

		# Set up directory tags list view model
		self.dirtagsListViewModel = QStringListModel()
		self.dirtagListView.setModel(self.dirtagsListViewModel)

		# Set up graphics view
		self.scene = QGraphicsScene()
		self.viewerGraphicsView.setScene(self.scene)
		self.viewerGraphicsView.setRenderHint(QPainter.RenderHint.Antialiasing)

		# Connect signals
		#self.actionExit.triggered.connect(self.close)
		#self.actionOpen.triggered.connect(self.open_directory)
		self.selectorListView.selectionModel().selectionChanged.connect(self.display_image)

		# Auto load image directory for testing
		#self.open_directory("./images")
		self.open_directory("***REMOVED***")

	def open_directory(self, directory: str | None = None):
		"""Open directory dialog and load images"""

		if not directory:

			directory = QFileDialog.getExistingDirectory(
				self, "Select Directory", "",
				QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
			)

			if not directory:
				return

		try:
			# Clear previous content
			self.selectorListViewModel.clear()

			# Supported image extensions
			image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}

			# Scan for images
			tag_images: list[TagImage] = []
			for file_path in Path(directory).iterdir():
				if file_path.is_file() and file_path.suffix.lower() in image_extensions:
					tag_images.append(TagImage(file_path))

			# Sort files alphabetically
			tag_images.sort()

			for image in tag_images:
				# Add images to selector
				item = QStandardItem(image.path.name)
				item.setData(image, Qt.ItemDataRole.UserRole)
				item.setIcon(image.thumbnail)
				self.selectorListViewModel.appendRow(item)

				# Collect unique tags for directory tags view
				self.directory_tags_set.update(image.tags)

			self.dirtagsListViewModel.setStringList(self.directory_tags_set)
			self.dirtagsListViewModel.sort(0, Qt.SortOrder.AscendingOrder)

			#self.statusbarMain.showMessage(f"Loaded {len(image_paths)} images")

		except Exception as e:
			QMessageBox.critical(self, "Error", f"Failed to load directory: {str(e)}")

	def display_image(self, selected_items: QItemSelectionRange, deselected_items):
		"""Display selected image in graphics view"""

		if not selected_items:
			return

		index = selected_items.indexes()[0]  # Take the first selected item

		tag_image:TagImage = self.selectorListViewModel.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)

		self.imgtagListViewModel.setStringList(tag_image.tags)

		path = str(tag_image.path)
		self.current_image_path = path

		try:
			pixmap = QPixmap(path)
			if pixmap.isNull():
				raise Exception("Failed to load image")

			# Clear previous scene and add new image
			self.scene.clear()
			self.scene.addPixmap(pixmap)

			self.viewerGraphicsView.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

		except Exception as e:
			QMessageBox.critical(self, "Error", f"Failed to display image: {str(e)}")


