from pathlib import Path

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QWidget

from src.config import Config, Setting


class RecentMenu(QMenu):
	def __init__(self, main_window: "MainWindow", *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._main_window = main_window
		self.max_entries = 10
		self.entries: list[str] = []

		self.setEnabled(False)

		saved_paths: list[str] = Config.read(Setting.RecentDirectories)
		if saved_paths:
			self.entries = saved_paths
			self.setEnabled(True)

		self.aboutToShow.connect(self.on_about_to_show)

	def add_entry(self, path: Path):
		while str(path) in self.entries:
			self.entries.remove(path)

		while len(self.entries) >= self.max_entries:
			self.entries.pop()

		self.entries.insert(0, path)
		Config.write(Setting.RecentDirectories, self.entries)
		self.setEnabled(True)

	def save_entries(self):
		Config.write(Setting.RecentDirectories, self.entries)

	def set_max_entries(self, max: int):
		self.max_entries = max

	def on_about_to_show(self):
		for action in self.actions():
			self.removeAction(action)

		for path in self.entries:
			action = QAction(path, self)
			action.setData(path)
			action.triggered.connect(self._main_window.on_open_recent)
			self.addAction(action)