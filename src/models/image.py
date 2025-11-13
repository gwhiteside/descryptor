import csv
import time
from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QImage, QPixmap


class TagEntry:
	def __init__(self, text: str = "", position: int = 0, modified: bool = False):
		self.text = text
		self.position = position
		self.modified = modified

	def __str__(self):
		return self.text


class Image:
	def __init__(self, path: Path):
		self.path = path
		self._thumbnail: QIcon | QImage | None = None
		self._preview: QIcon | QImage | None = None
		self.thumb_size: int = 0
		self.size: QSize | None = None
		self._tag_entries: list[TagEntry] | None = None # don't hold external references to _tag_entries
		self._modified: bool = False
		self._mtime: float = time.monotonic()
		self.test: TagEntry

	def __lt__(self, other):
		return self.path < other.path

	def append_tag(self, tag: str):
		self.insert_tag(tag, len(self._tag_entries))

	def insert_tag(self, tag: str, index: int):
		self._tag_entries.insert(index, TagEntry(tag, index, True))
		self.set_modified()

	def is_modified(self) -> bool:
		return self._modified

	def load_tags(self) -> list[TagEntry]:
		if self._tag_entries is not None:
			return self._tag_entries

		tag_path = self.path.with_suffix(".txt")
		if tag_path.exists():
			with tag_path.open(newline="") as file:
				self._tag_entries = [
					TagEntry(tag.strip(), index)
					for index, tag
					in enumerate(file.read().split(","))
				]
		else:
			self._tag_entries = []

		return self._tag_entries

	def remove_tag(self, tag: str):
		""" Removes **all** instances of ``tag``.
		"""
		# Create new list without removed tag
		self._tag_entries: list[TagEntry] = [s for s in self._tag_entries if s.text != tag]
		self.set_modified()

	def remove_tag_at(self, index: int) -> str:
		"""Removes tag at ``index``
		:param index: Index of tag to remove.
		:returns: The tag that was removed.
		"""
		tag_entry: TagEntry = self._tag_entries[index]
		del self._tag_entries[index]
		self.set_modified()
		return tag_entry.text

	def save_tags(self):
		tag_path = self.path.with_suffix(".txt")
		with open(tag_path, "w", newline="") as file:
			writer = csv.writer(file)
			writer.writerow(self.tags)
		""" TODO mark all saved objects as unmodified
		could just lean on the load routines, but
		- might be a bit riskier than setting items unmodified again? could break out those functions.
		vs
		- less likely to introduce future bugs
		"""

	def set_modified(self, is_modified: bool = True):
		"""Marks object as modified and records the time for sorting."""
		self._modified = is_modified
		self._mtime = time.monotonic() if is_modified else self._mtime

	@property
	def preview(self) -> QIcon | None:
		if type(self._preview) == QImage:
			self._preview = QIcon(QPixmap.fromImage(self._preview))
		return self._preview

	@preview.setter
	def preview(self, value: QIcon | QImage | None):
		self._preview = value

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