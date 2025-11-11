from PyQt6.QtWidgets import QCompleter, QLineEdit, QWidget


class Completer(QCompleter):
	def __init__(self):
		super().__init__()
		self._min_chars = 0

	def set_min_chars(self, min: int):
		self._min_chars = min

	def on_text_edited(self, text: str):
		if len(text) < self._min_chars:
			if self.popup().isVisible():
				self.popup().hide()
			return
		self.setCompletionPrefix(text)
		self.complete()

	# Overrides

	def setWidget(self, widget: QLineEdit | None):
		super().setWidget(widget)

		if widget is None:
			return

		widget.removeEventFilter(self)
		widget.textEdited.connect(self.on_text_edited)


"""
	self.line_edit.removeEventFilter(self)

	def min_char_completion(text):
		if len(text) >= 3:
			if self.line_edit.completer() is None:
				self.line_edit.setCompleter(completer)
		else:
			if self.line_edit.completer() is not None:
				self.line_edit.setCompleter(None)

	self.line_edit.textEdited.connect(min_char_completion)
"""