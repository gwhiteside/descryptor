import csv
import time
from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QImage, QPixmap


class Image:
	def __init__(self, path: Path):
		self.path = path
		self._thumbnail: QIcon | QImage | None = None
		self.thumb_size: int = 0
		self.size: QSize | None = None
		self._tags: list[str] | None = None # don't hold external references to _tags
		self._modified: bool = False
		self._mtime: float = time.monotonic()

	def __lt__(self, other):
		return self.path < other.path

	def insert_tag(self, tag: str, index: int):
		self._tags.insert(index, tag)
		self.set_modified()

	def is_modified(self) -> bool:
		return self._modified

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

	def remove_tag(self, tag: str):
		""" Removes **all** instances of ``tag``.
		"""
		# Create new list without removed tag
		self._tags = [s for s in self._tags if s != tag]
		self.set_modified()

	def remove_tag_at(self, index: int) -> str:
		"""Removes tag at ``index``
		:param index: Index of tag to remove.
		:returns: The string that was removed.
		"""
		tag: str = self._tags[index]
		del self._tags[index]
		self.set_modified()
		return tag

	def save_tags(self):
		tag_path = self.path.with_suffix(".txt")
		with open(tag_path, "w", newline="") as file:
			writer = csv.writer(file)
			writer.writerow(self.tags)

	def set_modified(self, is_modified: bool = True):
		"""Marks object as modified and records the time for sorting."""
		self._modified = is_modified
		self._mtime = time.monotonic() if is_modified else self._mtime

	@property
	def tags(self):
		return self.load_tags()

	@property
	def thumbnail(self) -> QIcon | None:
		if type(self._thumbnail) == QImage:
			self._thumbnail = QIcon(QPixmap.fromImage(self._thumbnail))
		return self._thumbnail

	@thumbnail.setter
	def thumbnail(self, value: QIcon | QImage | None):
		self._thumbnail = value