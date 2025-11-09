from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QHideEvent, QShowEvent
from PyQt6.QtWidgets import QDockWidget, QWidget, QHBoxLayout

from src.panels.swap_dock import SwapDock
from src.panels.tag_editor import TagEditorWidget
from src.panels.tag_index import TagIndexWidget


class UnifiedTagger(SwapDock):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

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

	def set_input_enabled(self, enabled: bool):
		self.tag_editor_widget.line_edit.setEnabled(enabled)

	def set_models(self, editor_model, index_model):
		self.tag_editor_widget.set_model(editor_model)
		self.tag_index_widget.set_model(index_model)

	# Overrides

	def forward_sources(self):
		return [self.tag_editor_widget, self.tag_index_widget]