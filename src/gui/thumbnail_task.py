from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot, Qt, QPoint, QRect, QSize
from PyQt6.QtGui import QImage

from models.image import Image


class ThumbnailLoader(QObject):
	thumbnail_ready = pyqtSignal(Image)

class ThumbnailTask(QRunnable):
	def __init__(self, image: Image, loader: ThumbnailLoader):
		super().__init__()
		self.image = image
		self.thumb_size = 200
		self.loader = loader

	@pyqtSlot()
	def run(self):
		# QPixmap uses the GUI thread, so load and scale with QImage
		qimage = QImage(str(self.image.path))
		if not qimage.isNull():
			self.image.size = qimage.size()
			qimage = qimage.scaled(
				self.thumb_size,
				self.thumb_size,
				Qt.AspectRatioMode.KeepAspectRatioByExpanding,
				Qt.TransformationMode.SmoothTransformation
			)
		self.image.preview = qimage

		top_left = QPoint(
			(qimage.width() - self.thumb_size) // 2,
			(qimage.height() - self.thumb_size) // 2
		)
		crop_rect = QRect(top_left, QSize(self.thumb_size, self.thumb_size))

		self.image.thumbnail = qimage.copy(crop_rect)
		self.loader.thumbnail_ready.emit(self.image)
