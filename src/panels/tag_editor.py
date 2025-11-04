from PyQt6.QtWidgets import QWidget, QListView, QVBoxLayout, QLineEdit


class TagEditor(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		main_vbox = QVBoxLayout()
		self.line_edit = QLineEdit()
		self.list_view = QListView()
		main_vbox.addWidget(self.line_edit)
		main_vbox.addWidget(self.list_view)

		self.setLayout(main_vbox)