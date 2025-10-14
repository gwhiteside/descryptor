import sys
from pathlib import Path
from PyQt6.QtWidgets import (
	QApplication, QGraphicsPixmapItem, QMainWindow, QListWidgetItem, QGraphicsScene,
	QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QPainter, QIcon
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		loadUi('src/main_window.ui', self)  # Load the UI file

		# Initialize variables
		self.current_image_path = None

		# Connect signals
		self.actionExit.triggered.connect(self.close)
		self.actionOpen.triggered.connect(self.open_directory)
		self.listImageSelect.itemSelectionChanged.connect(self.display_image)

		# Setup graphics view
		self.scene = QGraphicsScene()
		self.graphicsviewImage.setScene(self.scene)
		self.graphicsviewImage.setRenderHint(QPainter.RenderHint.Antialiasing)

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
			self.listImageSelect.clear()

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
				item = QListWidgetItem(path.name)
				item.setData(Qt.ItemDataRole.UserRole, str(path))

				# Create thumbnail
				pixmap = QPixmap(str(path))
				if not pixmap.isNull():
					# Scale thumbnail to fit (max 100x100)
					thumbnail = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
											Qt.TransformationMode.SmoothTransformation)
					item.setIcon(QIcon(thumbnail))
				else:
					# Fallback icon for failed images
					item.setIcon(QIcon())

				self.listImageSelect.addItem(item)

			self.statusbarMain.showMessage(f"Loaded {len(image_paths)} images")

		except Exception as e:
			QMessageBox.critical(self, "Error", f"Failed to load directory: {str(e)}")

	def display_image(self):
		"""Display selected image in graphics view"""
		# Get currently selected items
		selected_items = self.listImageSelect.selectedItems()
		if not selected_items:
			return

		item = selected_items[0]  # Take the first selected item
		path = item.data(Qt.ItemDataRole.UserRole)
		self.current_image_path = path

		try:
			# Load and display image
			pixmap = QPixmap(path)
			if pixmap.isNull():
				raise Exception("Failed to load image")

			# Clear previous scene and add new image
			self.scene.clear()

			pixmap_item = QGraphicsPixmapItem(pixmap)
			pixmap_item.setPos(-pixmap.width() / 2, -pixmap.height() / 2)
			self.scene.addPixmap(pixmap)

			#self.scene.setSceneRect(scene_rect)
			print("Scene dimensions: ", self.scene.width(), self.scene.height())
			self.graphicsviewImage.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)


		except Exception as e:
			QMessageBox.critical(self, "Error", f"Failed to display image: {str(e)}")

if __name__ == "__main__":
	app = QApplication(sys.argv)
	app.setApplicationName("descryptor33")
	app.setApplicationDisplayName("descryptor76")

	window = MainWindow()
	window.show()
	sys.exit(app.exec())
