from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QHideEvent, QShowEvent
from PyQt6.QtWidgets import QDockWidget, QWidget


class SwapDock(QDockWidget):
	data_changed = pyqtSignal()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.signals_connected = False

	def connect_signals(self):
		if self.signals_connected:
			return

		for widget in self.forward_sources():
			widget.data_changed.connect(self.on_data_changed)

		self.signals_connected = True

	def disconnect_signals(self):
		if not self.signals_connected:
			return

		for widget in self.forward_sources():
			widget.data_changed.disconnect(self.on_data_changed)

		self.signals_connected = False

	def on_data_changed(self):
		self.data_changed.emit()

	def forward_sources(self) -> list[QWidget]:
		"""Override to return iterable of child widgets whose data_changed signals should be forwarded."""
		return []

	# Overrides

	def hideEvent(self, event: QHideEvent):
		self.disconnect_signals()

	def showEvent(self, event: QShowEvent):
		self.connect_signals()