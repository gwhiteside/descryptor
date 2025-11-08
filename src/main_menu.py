from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import QMenu, QMainWindow, QMenuBar

from src.recent_menu import RecentMenu


def setup_menu(window: "MainWindow"):
	menu: QMenuBar = window.menuBar()

	file_menu = menu.addMenu("&File")

	open_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.FolderOpen), "&Open Directory", file_menu)
	open_action.triggered.connect(window.open_directory)
	file_menu.addAction(open_action)

	recent_menu = RecentMenu(window,"&Recent", file_menu)
	file_menu.addMenu(recent_menu)

	file_menu.addSeparator()

	save_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave), "&Save", file_menu)
	save_action.triggered.connect(window.save_tags)
	file_menu.addAction(save_action)

	file_menu.addSeparator()

	quit_action = QAction(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit), "&Quit", file_menu)
	quit_action.triggered.connect(window.close)
	file_menu.addAction(quit_action)

	view_menu = menu.addMenu("&View")

	show_selector_action = QAction("Show Image &Selector", view_menu)
	show_selector_action.setCheckable(True)
	show_selector_action.setChecked(True)
	view_menu.addAction(show_selector_action)

	show_viewer_action = QAction("Show Image &Viewer", view_menu)
	show_viewer_action.setCheckable(True)
	show_viewer_action.setChecked(True)
	view_menu.addAction(show_viewer_action)

	show_tag_editor_action = QAction("Show Tag &Editor", view_menu)
	show_tag_editor_action.setCheckable(True)
	show_tag_editor_action.setChecked(True)
	view_menu.addAction(show_tag_editor_action)

	show_tag_index_action = QAction("Show Tag &Index", view_menu)
	show_tag_index_action.setCheckable(True)
	show_tag_index_action.setChecked(True)
	view_menu.addAction(show_tag_index_action)

	view_menu.addSeparator()

	unified_tag_dock_action = QAction("Unified Tag Panel", view_menu)
	unified_tag_dock_action.setCheckable(True)
	unified_tag_dock_action.setChecked(False)
	unified_tag_dock_action.triggered.connect(window.toggle_unified_dock)
	view_menu.addAction(unified_tag_dock_action)

	# Create menu shortcuts

	open_action.setShortcut(QKeySequence.StandardKey.Open)
	quit_action.setShortcut(QKeySequence.StandardKey.Quit)
	save_action.setShortcut(QKeySequence.StandardKey.Save)

	# Create references

	window.recent_menu = recent_menu

