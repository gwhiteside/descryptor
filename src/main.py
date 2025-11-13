import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from settings.config import Config, APP_NAME

"""
Currently there's a library bug causing issues with Wayland.
For XDG_SESSION_TYPE=wayland set QT_QPA_PLATFORM=xcb for a less-buggy workaround.
"""


if __name__ == "__main__":
	QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

	application = QApplication(sys.argv)
	application.setApplicationDisplayName(APP_NAME)

	Config.initialize()

	window = MainWindow()
	window.show()

	sys.exit(application.exec())
