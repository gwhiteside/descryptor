from PyQt6.QtGui import QKeySequence


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
