from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QListView, QVBoxLayout, QLineEdit, QWidget, QCompleter

from src.completer import Completer
from src.models.image_tag_model import ImageTagModel
from src.models.tag_completer_model import TagCompleterModel
from src.panels.swap_dock import SwapDock


class TagEditorWidget(QWidget):
	data_changed = pyqtSignal()
	_completion_model: TagCompleterModel = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		vbox = QVBoxLayout()
		self.setLayout(vbox)

		self.line_edit = QLineEdit()
		self.list_view = QListView()

		vbox.addWidget(self.line_edit)
		vbox.addWidget(self.list_view)

		completer = Completer()
		if TagEditorWidget._completion_model is None:
			TagEditorWidget._completion_model = TagCompleterModel("data/danbooru.db")
		completer.setModel(TagEditorWidget._completion_model)
		completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)
		completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
		completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
		completer.setFilterMode(Qt.MatchFlag.MatchContains)
		completer.set_min_chars(3)
		#completer.setWidget(self.line_edit)

		self.line_edit.setCompleter(completer)

		self.line_edit.returnPressed.connect(self.add_tag)
		delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self.list_view)
		delete_shortcut.activated.connect(self.delete_selected_item)

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

	def delete_selected_item(self):
		indexes = self.list_view.selectedIndexes()
		if indexes:
			index = indexes[0]
			row = index.row()
			self.list_view.model().remove_tag_at(row)

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


class TagEditor(SwapDock):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

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

	def set_input_enabled(self, enabled: bool):
		self.tag_editor_widget.line_edit.setEnabled(enabled)

	def set_model(self, model):
		self.tag_editor_widget.set_model(model)

	# Overrides

	def forward_sources(self):
		return [self.tag_editor_widget]