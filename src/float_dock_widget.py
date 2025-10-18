from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget

class FloatDockWidget(QDockWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.topLevelChanged.connect(self.top_level_changed)

	def closeEvent(self, event):
		if self.isFloating():
			event.ignore()
			self.setFloating(False)
		else:
			super().closeEvent(event)

	def top_level_changed(self, top_level: bool):
		if top_level:
			self.setWindowFlags(Qt.WindowType.Window)
			self.show()