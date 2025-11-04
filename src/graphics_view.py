from PyQt6.QtCore import Qt, QSize, QThreadPool
from PyQt6.QtGui import QWheelEvent, QPixmap, QImage
from PyQt6.QtWidgets import QGraphicsView

from src.image import Image
from src.image_task import ImageLoader, ImageTask


class GraphicsView(QGraphicsView):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.current_zoom = 1.0
		self.zoom_factor = 1.5
		self.current_task: ImageTask | None = None

		self.loader = ImageLoader()
		self.loader.image_ready.connect(self.on_image_ready)

	def load_image(self, image: Image):
		pixmap = image.preview.pixmap(QSize(500,500)) # could be done better
		self.set_view(pixmap)

		if self.current_task:
			self.current_task.canceled = True

		self.current_task = ImageTask(image, self.loader)
		QThreadPool.globalInstance().start(self.current_task, 1)

	def on_image_ready(self, qimage: QImage):
		pixmap = QPixmap.fromImage(qimage)
		self.set_view(pixmap)

	def set_view(self, pixmap: QPixmap):
		self.scene().clear()
		self.scene().addPixmap(pixmap)
		self.current_zoom = 1.0
		self.setSceneRect(0, 0, pixmap.width(), pixmap.height())
		self.fitInView(self.scene().itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

	def wheelEvent(self, event: QWheelEvent)-> None:
		old_position = self.mapToScene(event.position().toPoint())

		# zoom out
		if event.angleDelta().y() < 0:
			if self.current_zoom > 1.0:
				self.scale(1/self.zoom_factor, 1/self.zoom_factor)
				self.current_zoom /= self.zoom_factor
		# zoom in
		else:
			if self.current_zoom < 16.0:
				self.scale(self.zoom_factor, self.zoom_factor)
				self.current_zoom *= self.zoom_factor

		new_position = self.mapToScene(event.position().toPoint())
		delta = new_position - old_position
		self.translate(delta.x(), delta.y())
