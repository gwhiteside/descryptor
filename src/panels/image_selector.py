from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListView


class ImageSelector(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.listview = QListView()

		layout = QVBoxLayout()
		layout.addWidget(self.listview)

		self.setLayout(layout)

		self.listview.setIconSize(QSize(150, 150))
		self.listview.setGridSize(QSize(180, 180))
		self.listview.setSpacing(8)
		self.listview.setViewMode(QListView.ViewMode.IconMode)
		self.listview.setResizeMode(QListView.ResizeMode.Adjust)
		self.listview.setUniformItemSizes(True)
