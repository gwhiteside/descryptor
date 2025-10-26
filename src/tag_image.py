import time
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon

class TagImage:
	def __init__(self, path: Path):
		self.path = path
		self._thumbnail: QIcon | None = None
		self.thumb_size: int = 0
		self._tags: list[str] | None = None
		self.modified: bool = False
		self.m_time: float = time.monotonic()

	def __lt__(self, other):
		return self.path < other.path

	def load_thumbnail(self, size: int = 200) -> QIcon:
		if self._thumbnail is not None and self.thumb_size == size:
			return self._thumbnail

		pixmap = QPixmap(str(self.path))
		if pixmap.isNull():
			self._thumbnail = QIcon()
		else:
			thumbnail = pixmap.scaled(
				size, # width
				size, # height
				Qt.AspectRatioMode.KeepAspectRatio, # aspectRatioMode
				Qt.TransformationMode.SmoothTransformation # transformMode
			)
			self._thumbnail = QIcon(thumbnail)
			self.thumb_size = size

		return self._thumbnail

	def load_tags(self) -> list[str]:
		if self._tags is not None:
			return self._tags

		tag_path = self.path.with_suffix(".txt")
		if tag_path.exists():
			with tag_path.open(newline="") as file:
				self._tags = [tag.strip() for tag in file.read().split(",")]
		else:
			self._tags = []

		return self._tags

	def add_tag(self, tag: str):
		if tag not in self._tags:
			self._tags.append(tag)
			self.modified = True

	@property
	def thumbnail(self):
		return self.load_thumbnail()

	@property
	def tags(self):
		return self.load_tags()