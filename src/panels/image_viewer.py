from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QComboBox, QSizePolicy

from src.graphics_view import GraphicsView


class ImageViewer(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setObjectName("image_viewer")

		main_vbox = QVBoxLayout()

		self.gfx_view = GraphicsView()

		controls_hbox = QHBoxLayout()
		self.zoom_slider = QSlider()
		self.zoom_slider.setOrientation(Qt.Orientation.Horizontal)
		self.zoom_cbox = QComboBox()
		controls_hbox.addWidget(self.zoom_slider)
		controls_hbox.addWidget(self.zoom_cbox)

		main_vbox.addWidget(self.gfx_view)
		main_vbox.addLayout(controls_hbox)

		self.setLayout(main_vbox)