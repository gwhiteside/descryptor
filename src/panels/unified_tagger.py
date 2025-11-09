from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QHideEvent, QShowEvent
from PyQt6.QtWidgets import QDockWidget, QWidget, QHBoxLayout

from src.panels.tag_editor import TagEditorWidget
from src.panels.tag_index import TagIndexWidget


class UnifiedTagger(QDockWidget):
	data_changed = pyqtSignal()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.signals_connected = False

		self.setObjectName("unified_tagger")

		main_widget = QWidget()
		hbox = QHBoxLayout()
		main_widget.setLayout(hbox)

		self.tag_editor_widget = TagEditorWidget()
		self.tag_index_widget = TagIndexWidget()

		hbox.addWidget(self.tag_editor_widget, 1)
		hbox.addWidget(self.tag_index_widget, 1)
		hbox.setContentsMargins(0, 0, 0, 0)
		hbox.setSpacing(0)

		self.setWidget(main_widget)

		self.set_input_enabled(False) # enabled once something is loaded

	def clear_input(self):
		self.tag_editor_widget.line_edit.clear()

	def connect_signals(self):
		if not self.signals_connected:
			print(self.objectName() + " signal connected")
			self.tag_editor_widget.data_changed.connect(self.on_data_changed)
			self.signals_connected = True

	def disconnect_signals(self):
		if self.signals_connected:
			print(self.objectName() + " signal disconnected")
			self.tag_editor_widget.data_changed.disconnect(self.on_data_changed)
			self.signals_connected = False

	def on_data_changed(self):
		print(self.objectName() + " on_data_changed")
		self.data_changed.emit()

	def set_input_enabled(self, enabled: bool):
		self.tag_editor_widget.line_edit.setEnabled(enabled)

	def set_models(self, editor_model, index_model):
		self.tag_editor_widget.set_model(editor_model)
		self.tag_index_widget.set_model(index_model)

	# Overrides

	def hideEvent(self, event: QHideEvent):
		self.disconnect_signals()

	def showEvent(self, event: QShowEvent):
		self.connect_signals()