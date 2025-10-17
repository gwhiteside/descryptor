import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
	application = QApplication(sys.argv)

	application.setApplicationName("descryptor")
	application.setApplicationDisplayName("Select Folder")

	window = MainWindow()
	window.show()

	sys.exit(application.exec())
