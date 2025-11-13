from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QVBoxLayout, QListView, QDockWidget, QWidget


class ImageSelector(QDockWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setObjectName("image_selector")

		main_widget = QWidget()
		vbox = QVBoxLayout()
		main_widget.setLayout(vbox)

		self.listview = QListView()

		vbox.addWidget(self.listview)

		self.setWidget(main_widget)

		self.listview.setIconSize(QSize(150, 150))
		self.listview.setGridSize(QSize(180, 180))
		self.listview.setSpacing(8)
		self.listview.setViewMode(QListView.ViewMode.IconMode)
		self.listview.setResizeMode(QListView.ResizeMode.Adjust)
		self.listview.setUniformItemSizes(True)
