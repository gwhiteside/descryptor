from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget

from src.config import Config


SHORTCUTS = {
	# Global

	"next_image": "Ctrl+N",
	"previous_image": "Ctrl+P",

	# List views

	"delete_item": QKeySequence.StandardKey.Delete,

	# Menu

	"open_file": QKeySequence.StandardKey.Open,
	"quit_application": QKeySequence.StandardKey.Quit,
	"save_directory": QKeySequence.StandardKey.Save,
}
