import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow


"""
Currently there's a library bug causing issues with Wayland.
Set XDG_SESSION_TYPE=wayland and QT_QPA_PLATFORM=xcb for a less-buggy workaround.
"""


if __name__ == "__main__":
	QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
	application = QApplication(sys.argv)

	application.setApplicationName("descryptor")
	application.setApplicationDisplayName("Select Folder")

	window = MainWindow()
	window.show()

	sys.exit(application.exec())
