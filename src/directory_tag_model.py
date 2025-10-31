from collections import Counter

from PyQt6.QtCore import QAbstractItemModel, QAbstractListModel, QModelIndex, Qt
from PyQt6.QtGui import QColor, QFont

from src.image_tag_model import ImageTagModel
from src.tag_image import TagImage
from src.tag_image_directory import TagImageDirectory


class DirectoryTagModel(QAbstractListModel):
	def __init__(self, directory: TagImageDirectory | None = None):
		super().__init__()
		self.directory = None
		self.current_image: TagImage | None = None
		self.tag_map: dict[str, list[TagImage]] = {} # inverted index of tags to TagImages
		self.__view_cache: list[str] = [] # cached sorted tags (with values) from tag_map
		self.load(directory)

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

	def decrement_tag(self, tag: str):
		# images = self.tag_map.pop(tag, None)
		# if not images:
		# 	return
		# for image in images:
		# 	image.tags.remove(tag)
		# 	image.modified = True

		t: list[TagImage] = self.tag_map[tag]


		# match role:
		# 	# case Qt.ItemDataRole.BackgroundRole:
		# 	# 	return self.changed_background if tag_image.modified else None
		# 	# case Qt.ItemDataRole.DecorationRole:
		# 	# 	return tag_image.thumbnail
		# 	case Qt.ItemDataRole.DisplayRole:
		# 		return tag
		# 	case Qt.ItemDataRole.EditRole:
		# 		return tag
		# 	case Qt.ItemDataRole.FontRole:
		#
		# 	case Qt.ItemDataRole.ForegroundRole:
		# 		if self.current_image is not None:
		# 			if tag in self.current_image.tags:
		# 				return QColor("green")
		#
		# 		return None
		# 	# case Qt.ItemDataRole.UserRole:
		# 	# 	return tag_image
		# 	case _:
		# 		return None

	def load(self, directory: TagImageDirectory):
		if directory is None:
			return
		self.directory = directory
		self._build_tag_map()

	def on_image_loaded(self, image: TagImage):
		self.current_image = image
		self.dataChanged.emit(QModelIndex(), QModelIndex(), [Qt.ItemDataRole.ForegroundRole])

	def on_image_tags_modified(self, image: TagImage, old_tags: set[str], new_tags: set[str]):
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

	def on_tag_removed(self, tag: str):
		image_tag_model: ImageTagModel = self.sender()
		tag_images: list[TagImage] = self.tag_map[tag]
		tag_images.remove(image_tag_model.tag_image)
		self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(0, 0), [Qt.ItemDataRole.DisplayRole])

	def remove_tag(self, tag: str):
		"""Removes all instances of ``tag`` from all ``TagImage`` instances."""
		images = self.tag_map.pop(tag, None)
		if not images:
			return
		for image in images:
			image.remove_tag(tag)
			# TODO data should inform their views of change here
		# TODO inform this model's views of data change

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
		for image in self.directory.tag_images:
			for tag in image.tags:
				self.tag_map.setdefault(tag, []).append(image)

		self._build_tag_cache()


	#
	# class TagTracker:
	# 	def __init__(self):
	# 		self.tag_refs: dict[str, list[TagImage]] = {}
	#
	# 	def add_ref(self, tag: str, image: TagImage):
	# 		value = self.tag_refs.get(tag)
	# 		if value is None:
	# 			self.tag_refs[tag] = [image] # first instance of tag
	# 		else:
	# 			self.tag_refs[tag].append(image) # add image to list of refs
	#
	# 	def remove_ref(self, tag: str, image: TagImage):
	# 		value = self.tag_refs.get(tag)
	# 		if value is None:
	# 			# This shouldn't happen
	# 			return
	# 		elif len(value) == 0:
	# 			# This also shouldn't happen
	# 			return
	# 		elif len(value) == 1:
	# 			del self.tag_refs[tag]
	# 		else:
	# 			value.remove(image)
