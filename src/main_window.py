from pathlib import Path

from PyQt6.QtCore import QItemSelectionRange, Qt
from PyQt6.QtGui import QPixmap, QPainter, QIcon, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
	QMainWindow, QGraphicsScene,
	QFileDialog, QMessageBox, QListView, QGraphicsView
)
from PyQt6.uic import loadUi

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		# Load interface
		loadUi('src/main_window.ui', self)
		self.imageGraphicsView: QGraphicsView = self.findChild(QGraphicsView, "imageGraphicsView")
		self.imageListView: QListView = self.findChild(QListView, "imageListView")

		# Connect signals
		self.actionExit.triggered.connect(self.close)
		self.actionOpen.triggered.connect(self.open_directory)
		self.imageListView.selectionModel().selectionChanged.connect(self.display_image)

		# Setup list view
		self.imageListViewModel = QStandardItemModel()
		self.imageListView.setModel(self.imageListViewModel)

		# Setup graphics view
		self.scene = QGraphicsScene()
		self.imageGraphicsView.setScene(self.scene)
		self.imageGraphicsView.setRenderHint(QPainter.RenderHint.Antialiasing)

		# Instance variables
		self.current_image_path = None

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
			self.imageListViewModel.clear()

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

				self.imageListViewModel.appendRow(item)

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
		path = self.imageListViewModel.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)
		self.current_image_path = path

		try:
			pixmap = QPixmap(path)
			if pixmap.isNull():
				raise Exception("Failed to load image")

			# Clear previous scene and add new image
			self.scene.clear()
			self.scene.addPixmap(pixmap)

			self.imageGraphicsView.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

		except Exception as e:
			QMessageBox.critical(self, "Error", f"Failed to display image: {str(e)}")
