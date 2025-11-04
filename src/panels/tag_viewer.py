from PyQt6.QtWidgets import QWidget, QListView, QVBoxLayout


class TagViewer(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.listview = QListView()

		layout = QVBoxLayout()
		layout.addWidget(self.listview)

		self.setLayout(layout)