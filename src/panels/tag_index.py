from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QListView, QVBoxLayout, QWidget

from src.panels.swap_dock import SwapDock


class TagIndexWidget(QWidget):
	data_changed = pyqtSignal()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		vbox = QVBoxLayout()
		self.setLayout(vbox)

		self.list_view = QListView()

		vbox.addWidget(self.list_view)

	def on_data_changed(self):
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

class TagIndex(SwapDock):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setObjectName("tag_index")
		self.tag_index_widget = TagIndexWidget()
		self.setWidget(self.tag_index_widget)

	# def clear_model(self):
	# 	model: DirectoryImageModel = self.tag_index_widget.list_view.model()
	# 	if model is not None:
	# 		# clear model

	def set_model(self, model):
		self.tag_index_widget.set_model(model)

	# Overrides

	def forward_sources(self):
		return [self.tag_index_widget]