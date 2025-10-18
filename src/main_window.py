from pathlib import Path

from PyQt6.QtCore import QItemSelectionRange, Qt
from PyQt6.QtGui import QPixmap, QPainter, QIcon, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
	QMainWindow, QGraphicsScene,
	QFileDialog, QMessageBox, QListView, QGraphicsView, QDockWidget
)
from PyQt6.uic import loadUi

from src.float_dock_widget import FloatDockWidget
from src.graphics_view import GraphicsView


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		# Instance variables
		self.current_image_path = None

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

		# Setup dock widgets
		self.splitDockWidget(self.selectorDockWidget, self.viewerDockWidget, Qt.Orientation.Horizontal)
		self.splitDockWidget(self.viewerDockWidget, self.imgtagsDockWidget, Qt.Orientation.Horizontal)
		self.splitDockWidget(self.imgtagsDockWidget, self.dirtagsDockWidget, Qt.Orientation.Horizontal)

		# Setup list view
		self.selectorListViewModel = QStandardItemModel()
		self.selectorListView.setModel(self.selectorListViewModel)

		# Setup graphics view
		self.scene = QGraphicsScene()
		self.viewerGraphicsView.setScene(self.scene)
		self.viewerGraphicsView.setRenderHint(QPainter.RenderHint.Antialiasing)

		# Connect signals
		#self.actionExit.triggered.connect(self.close)
		#self.actionOpen.triggered.connect(self.open_directory)
		self.selectorListView.selectionModel().selectionChanged.connect(self.display_image)

		# Auto load image directory for testing
		self.open_directory("./images")

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
			image_paths = []
			for file_path in Path(directory).iterdir():
				if file_path.is_file() and file_path.suffix.lower() in image_extensions:
					image_paths.append(file_path)

			# Sort files alphabetically
			image_paths.sort()

			# Add thumbnails to list
			for path in image_paths:
				item = QStandardItem(path.name)
				item.setData(str(path), Qt.ItemDataRole.UserRole)

				# Create thumbnail
				pixmap = QPixmap(str(path))
				if not pixmap.isNull():
					# Scale thumbnail
					thumbnail = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
					item.setIcon(QIcon(thumbnail))
				else:
					# Fallback icon for failed images
					item.setIcon(QIcon())

				self.selectorListViewModel.appendRow(item)

			#self.statusbarMain.showMessage(f"Loaded {len(image_paths)} images")

		except Exception as e:
			QMessageBox.critical(self, "Error", f"Failed to load directory: {str(e)}")

	def display_image(self, selected_items: QItemSelectionRange, deselected_items):
		"""Display selected image in graphics view"""
		# Get currently selected items
		#selected_items = self.listImageSelect.selectedItems()

		if not selected_items:
			return

		index = selected_items.indexes()[0]  # Take the first selected item
		#path = item.data(Qt.ItemDataRole.UserRole)
		path = self.selectorListViewModel.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)
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
