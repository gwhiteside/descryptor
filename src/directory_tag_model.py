from collections import Counter

from PyQt6.QtCore import QAbstractItemModel, QAbstractListModel, QModelIndex, Qt
from PyQt6.QtGui import QColor, QFont

from src.image_tag_model import ImageTagModel
from src.image import Image
from src.directory import Directory


class DirectoryTagModel(QAbstractListModel):
	def __init__(self, directory: Directory | None = None):
		super().__init__()
		self.directory = None
		self.current_image: Image | None = None
		self.tag_map: dict[str, list[Image]] = {} # inverted index of tags to TagImages
		self.__view_cache: list[str] = [] # cached sorted tags (with values) from tag_map
		self.load(directory)

	def load(self, directory: Directory):
		if directory is None:
			return

		self.layoutAboutToBeChanged.emit()
		self.directory = directory
		self._build_tag_map()
		self.layoutChanged.emit()

	def on_image_loaded(self, image: Image):
		self.current_image = image
		self.dataChanged.emit(QModelIndex(), QModelIndex(), [Qt.ItemDataRole.ForegroundRole])

	def on_image_tags_modified(self, image: Image, old_tags: Counter[str], new_tags: Counter[str]):
		added = new_tags - old_tags
		removed = old_tags - new_tags

		for tag in added:
			self.tag_map.setdefault(tag, []).append(image)

		for tag in removed:
			images = self.tag_map.get(tag)
			if images:
				images.remove(image)
				if not images:
					del self.tag_map[tag]

		# could optimize a bit, but rebuilding the whole mostly-sorted cache is fine
		self._build_tag_cache()
		self.dataChanged.emit(QModelIndex(), QModelIndex(), [Qt.ItemDataRole.DisplayRole])

	def on_tag_removed(self, tag: str):
		image_tag_model: ImageTagModel = self.sender()
		images: list[Image] = self.tag_map[tag]
		images.remove(image_tag_model.image)
		self.dataChanged.emit(self.index(0, 0), self.index(0, 0), [Qt.ItemDataRole.DisplayRole])

	def remove_tag(self, tag: str):
		"""Removes all instances of ``tag`` from all ``TagImage`` instances."""
		images = self.tag_map.pop(tag, None)
		if not images:
			return
		for image in images:
			image.remove_tag(tag)
			# TODO data should inform their views of change here
		# TODO inform this model's views of data change

	# ---- Overrides

	def data(self, index: QModelIndex, role: int):
		tag = self.__view_cache[index.row()]

		q = Qt.ItemDataRole

		if role == q.DisplayRole:
			tag_count = len(self.tag_map[tag])
			display_string = f"{tag} ({tag_count})"
			return display_string
		if role == q.EditRole:
			return tag

		if self.current_image is None:
			return None

		if role == q.FontRole:
			testfont = QFont()
			testfont.setBold(True)
			return testfont if tag in self.current_image.tags else QFont()
		if role == q.ForegroundRole:
			return QColor("green") if tag in self.current_image.tags else None

		return None

	def rowCount(self, index: QModelIndex):
		return len(self.tag_map)

	# --- Private methods

	def _build_tag_cache(self):
		self.tag_map = dict(sorted(self.tag_map.items()))
		self.__view_cache = list(self.tag_map)

	def _build_tag_map(self):
		if self.directory is None:
			return

		self.tag_map.clear()
		for image in self.directory.images:
			for tag in image.tags:
				self.tag_map.setdefault(tag, []).append(image)

		self._build_tag_cache()
