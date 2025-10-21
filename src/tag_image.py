import time
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon

LAZY: bool = False

class TagImage:
	def __init__(self, path: Path):
		self.path = path
		self._thumbnail: QIcon | None = None
		self._tags: list[str] | None = None
		self._modified: bool = False
		self._mtime: float = time.monotonic()

		#if not LAZY:
		#	self.thumbnail

	def __lt__(self, other):
		return self.path < other.path

	@property
	def thumbnail(self):
		if not self._thumbnail:
			pixmap = QPixmap(str(self.path))
			if pixmap.isNull():
				self._thumbnail = QIcon()
			else:
				self._thumbnail = QIcon(pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

		return self._thumbnail

	@property
	def tags(self):
		if not self._tags:
			tag_path = self.path.with_suffix(".txt")
			if tag_path.exists():
				with tag_path.open(newline="") as file:
					self._tags = file.read().split(",")
			else:
				self._tags = []
		return self._tags