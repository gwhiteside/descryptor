from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot, Qt
from PyQt6.QtGui import QImage

from src.image import Image


class ImageLoader(QObject):
	image_ready = pyqtSignal(QImage)

class ImageTask(QRunnable):
	def __init__(self, image: Image, loader: ImageLoader):
		super().__init__()
		self.image = image
		self.loader = loader
		self.canceled = False

	@pyqtSlot()
	def run(self):
		if not self.canceled:
			qimage = QImage(str(self.image.path))
		if not self.canceled:
			self.loader.image_ready.emit(qimage)
