from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import QGraphicsView

class GraphicsView(QGraphicsView):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.current_zoom = 1.0
		self.zoom_factor = 1.5

	# def mouseMoveEvent(self, event: QMouseEvent) -> None:
 #
	# 	if event.buttons() == Qt.MouseButton.LeftButton:
	# 		delta = event.position() - self.last_position
	# 		self.last_position = event.position()
	# 		scene_rect = self.sceneRect()
	# 		transform = self.transform()
	# 		scene_rect.translate(-delta.x() / transform.m11(), -delta.y() / transform.m22())
	# 		self.setSceneRect(scene_rect)
	# 	else:
	# 		super().mouseMoveEvent(event)
 #
	# def mousePressEvent(self, event: QMouseEvent) -> None:
 #
	# 	if event.buttons() == Qt.MouseButton.LeftButton:
	# 		self.last_position = event.position()
	# 	else:
	# 		super().mouseMoveEvent(event)

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
