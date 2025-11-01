from pathlib import Path

from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QPixmap, QIcon, QImage

from src.image import Image


class ThumbnailLoader(QObject):
	thumbnail_ready = pyqtSignal(Image)

class ThumbnailTask(QRunnable):
	def __init__(self, image: Image, loader: ThumbnailLoader):
		super().__init__()
		self.image = image
		self.loader = loader

	@pyqtSlot()
	def run(self):
		# QPixmap uses the GUI thread, so load and scale with QImage
		qimage = QImage(str(self.image.path))
		if not qimage.isNull():
			self.image.size = qimage.size()
			qimage = qimage.scaled(
				200,  # self.size,  # width
				200,  # self.size,  # height
				Qt.AspectRatioMode.KeepAspectRatio,  # aspectRatioMode
				Qt.TransformationMode.SmoothTransformation  # transformMode
			)
		self.image.thumbnail = qimage
		self.loader.thumbnail_ready.emit(self.image)
