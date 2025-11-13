from PyQt6.QtCore import pyqtSignal, Qt, QSortFilterProxyModel, QModelIndex
from PyQt6.QtGui import QShortcut, QKeySequence, QTextOption
from PyQt6.QtWidgets import QListView, QVBoxLayout, QLineEdit, QWidget, QCompleter, QAbstractScrollArea, QTableView, \
	QAbstractItemView, QHeaderView

from models.image_tag_model import ImageTagModel
from models.tag_completer_model import TagCompleterModel
from gui.swap_dock import SwapDock


class SortProxy(QSortFilterProxyModel):
	def __init__(self):
		super().__init__()

	def lessThan(self, left: QModelIndex, right: QModelIndex):
		column = left.column()
		left_data = self.sourceModel().data(left)
		right_data = self.sourceModel().data(right)

		if column == 1: # count column
			return int(left_data) > int(right_data)
		return str(left_data) < str(right_data)


class TagEditorWidget(QWidget):
	data_changed = pyqtSignal()
	_completion_model: TagCompleterModel = None
	_alpha_completer: QCompleter = None
	_count_completer: QCompleter = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.db_path = "data/danbooru.db"

		vbox = QVBoxLayout()
		self.setLayout(vbox)

		self.line_edit = QLineEdit()
		self.list_view = QListView()

		vbox.addWidget(self.line_edit)
		vbox.addWidget(self.list_view)

		completer = self._count_completer_instance()
		#completer = QCompleter()
		#completer.setModel(model)
		completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)
		completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
		completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
		completer.setFilterMode(Qt.MatchFlag.MatchContains)
		completer.setMaxVisibleItems(10)

		table_view = QTableView()
		completer.setPopup(table_view)
		table_view.horizontalHeader().setVisible(False)
		table_view.setShowGrid(False)
		table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
		metrics = table_view.fontMetrics()
		model = self._completion_model_instance()

		tag_width = metrics.averageCharWidth() * model.get_top_percentile_tag_len(99)
		count_width = metrics.averageCharWidth() * (model.get_max_count_len() + 1)
		#table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		#table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

		table_view.setFixedWidth(tag_width + count_width)
		table_view.setWordWrap(False)
		row_height = metrics.height()
		table_view.verticalHeader().setMinimumSectionSize(row_height)
		table_view.verticalHeader().setDefaultSectionSize(row_height)

		table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
		table_view.setColumnWidth(0, tag_width)
		table_view.setColumnWidth(1, count_width)
		table_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
		table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
		#table_view.setGridStyle(Qt.PenStyle.NoPen)


		popup = completer.popup()
		#popup.setUniformItemSizes(True) # greatly increases responsiveness for free here
		#popup.setMinimumSize
		#popup.setLayoutMode(QListView.LayoutMode.Batched) # greatly increases responsiveness, but flickers
		#popup.setBatchSize(100)

		self.line_edit.setCompleter(completer) # don't forget to do this if not using on_text_edited hack

		def on_text_edited(text):
			"""Intended to restrict matching to minimum number of characters, but performance is
			very good regardless, so it's a matter of taste now."""
			if len(text) >= 1:
				if self.line_edit.completer() is None:
					self.line_edit.setCompleter(completer)
			else:
				if self.line_edit.completer() is not None:
					self.line_edit.setCompleter(None)

		#self.line_edit.textEdited.connect(on_text_edited)

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

	def _alpha_completer_instance(self):
		if TagEditorWidget._alpha_completer is None:
			proxy = SortProxy()
			proxy.setSourceModel(self._completion_model_instance())
			# proxy.setDynamicSortFilter(True)
			# proxy.setFilterKeyColumn(0)
			# proxy.sort(0, Qt.SortOrder.AscendingOrder)

			completer = QCompleter()
			completer.setModel(proxy)
			completer.setCompletionColumn(0)
			completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

			TagEditorWidget._alpha_completer = completer

		return TagEditorWidget._alpha_completer

	def _completion_model_instance(self):
		if TagEditorWidget._completion_model is None:
			TagEditorWidget._completion_model = TagCompleterModel(self.db_path)

		return TagEditorWidget._completion_model

	def _count_completer_instance(self):
		if TagEditorWidget._count_completer is None:
			proxy = SortProxy()
			proxy.setSourceModel(self._completion_model_instance())
			proxy.sort(1, Qt.SortOrder.AscendingOrder)

			completer = QCompleter()
			completer.setModel(proxy)
			completer.setCompletionColumn(0)
			completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

			TagEditorWidget._count_completer = completer

		return TagEditorWidget._count_completer


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