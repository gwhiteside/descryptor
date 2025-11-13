from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QSlider, QComboBox, QSizePolicy, QDockWidget, QWidget

from gui.graphics_view import GraphicsView


class ImageViewer(QDockWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setObjectName("image_viewer")

		main_widget = QWidget()
		vbox = QVBoxLayout()
		main_widget.setLayout(vbox)

		self.gfx_view = GraphicsView()

		controls_hbox = QHBoxLayout()
		self.zoom_slider = QSlider()
		self.zoom_slider.setOrientation(Qt.Orientation.Horizontal)
		self.zoom_cbox = QComboBox()
		controls_hbox.addWidget(self.zoom_slider)
		controls_hbox.addWidget(self.zoom_cbox)

		vbox.addWidget(self.gfx_view)
		vbox.addLayout(controls_hbox)

		self.setWidget(main_widget)