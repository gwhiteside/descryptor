from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QShowEvent, QHideEvent
from PyQt6.QtWidgets import QListView, QVBoxLayout, QLineEdit, QDockWidget, QWidget

from src.image_tag_model import ImageTagModel


class TagEditorWidget(QWidget):
	data_changed = pyqtSignal()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		vbox = QVBoxLayout()
		self.setLayout(vbox)

		self.line_edit = QLineEdit()
		self.list_view = QListView()

		vbox.addWidget(self.line_edit)
		vbox.addWidget(self.list_view)

		self.line_edit.returnPressed.connect(self.add_tag)

	def add_tag(self):
		text = self.line_edit.text().strip()
		if not text:
			return

		indexes = self.list_view.selectedIndexes()
		model = self.list_view.model()
		if len(indexes) > 0:
			index = indexes[0]
			model.insert_tag(text, index.row())
			self.list_view.setCurrentIndex(index)
		else:
			model.append_tag(text)

		self.line_edit.clear()

	def on_data_changed(self):
		print("child on_data_changed")
		self.data_changed.emit()

	def set_model(self, model):
		old_model = self.list_view.model()
		if old_model is not None:
			old_model.dataChanged.disconnect(self.on_data_changed)
			old_model.rowsInserted.disconnect(self.on_data_changed)
			old_model.rowsRemoved.disconnect(self.on_data_changed)

		self.list_view.setModel(model)
		model.dataChanged.connect(self.on_data_changed)
		model.rowsInserted.connect(self.on_data_changed)
		model.rowsRemoved.connect(self.on_data_changed)


class TagEditor(QDockWidget):
	data_changed = pyqtSignal()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.signals_connected = False

		self.setObjectName("tag_editor")
		self.tag_editor_widget = TagEditorWidget()
		self.setWidget(self.tag_editor_widget)

		self.set_input_enabled(False) # enabled once something is loaded

	def clear_input(self):
		self.tag_editor_widget.line_edit.clear()

	def clear_model(self):
		model: ImageTagModel = self.tag_editor_widget.list_view.model()
		if model is not None:
			model.clear()

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

	def set_model(self, model):
		self.tag_editor_widget.set_model(model)

	# Overrides

	def hideEvent(self, event: QHideEvent):
		self.disconnect_signals()

	def showEvent(self, event: QShowEvent):
		self.connect_signals()
