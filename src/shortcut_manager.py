from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget

from src.config import Config
from src.shortcuts import SHORTCUTS


class ShortcutManager:
	_instance = None

	def __init__(self):
		self.defaults = SHORTCUTS
		self.active = self._load_shortcuts()

	@classmethod
	def instance(cls):
		if cls._instance is None:
			cls._instance = cls()
		return cls._instance

	def _load_shortcuts(self):
		active = {}
		for name, default in self.defaults.items():
			value = Config.read(f"Shortcuts/{name}")
			active[name] = QKeySequence(value) if value else QKeySequence(default)
		return active

	def save_shortcuts(self):
		for key, value in self.active.items():
			name: str = key
			sequence: QKeySequence = value
			Config.write(f"Shortcuts/{name}", sequence.toString())

	def get(self, name: str):
		return self.active[name]

	def create(self, name: str, parent: QWidget, slot) -> QShortcut:
		sequence = self.get(name)
		shortcut = QShortcut(sequence, parent)
		shortcut.activated.connect(slot)
		return shortcut

	def set(self, name: str, sequence):
		self.active[name] = QKeySequence(sequence)
		self.save_shortcuts()