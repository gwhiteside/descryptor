from dataclasses import dataclass, field

from PyQt6.QtCore import QAbstractItemModel, QAbstractListModel, Qt, QModelIndex, pyqtSignal
from PyQt6.QtGui import QBrush, QColor

from src.tag_image import TagImage

class ImageTagModel(QAbstractListModel):
	tagsModified = pyqtSignal(TagImage)

	def __init__(self, tag_image: TagImage | None = None):
		super().__init__()
		self.tag_image = tag_image
		self.new_tags: list[str] = []
		self.changed_background = QBrush(QColor(128, 0, 0, 50))

	def appendTag(self, tag: str):
		self.tag_image.add_tag(tag)
		self.new_tags.append(tag)
		index = self.index(len(self.tag_image.tags) - 1)
		self.dataChanged.emit(index, index)
		self.tagsModified.emit(self.tag_image)

	def setTagImage(self, tag_image: TagImage):
		self.beginResetModel()
		self.tag_image = tag_image
		self.endResetModel()

	# overrides

	def data(self, index: QModelIndex, role: int):
		tag = self.tag_image.tags[index.row()]

		q = Qt.ItemDataRole
		match role:
			# case Qt.ItemDataRole.BackgroundRole:
			# 	return self.changed_background if tag_image.modified else None
			# case Qt.ItemDataRole.DecorationRole:
			# 	return tag_image.thumbnail
			case q.DisplayRole:
				return tag
			case q.EditRole:
				return tag
			case q.ForegroundRole:
				if tag in self.new_tags:
					return QColor("red")
				else:
					return None
			# case Qt.ItemDataRole.UserRole:
			# 	return tag_image
			case _:
				return None

	def flags(self, index):
		#return super().flags(index)
		return (
			Qt.ItemFlag.ItemIsEnabled |
			Qt.ItemFlag.ItemIsSelectable |
			Qt.ItemFlag.ItemIsEditable
		)

	def rowCount(self, index: QModelIndex):
		if self.tag_image is None:
			return 0
		else:
			return len(self.tag_image.tags)

	def setData(self, index, value, role=...):
		return super().setData(index, value, role)


# class ImageTagModel2(QAbstractItemModel):
# 	def __init__(self, tag_image: TagImage | None = None, view_mode: str = "flat"):
# 		super().__init__()
# 		self.tag_image = tag_image
# 		self.view_mode = view_mode # "flat" or "tree"
# 		self.root = ImageTagModel.Node("<root>")
# 		if tag_image:
# 			self._build_tree()
#
# 	def _build_tree(self):
# 		self.beginResetModel()
# 		self.root.children.clear()
# 		if not self.tag_image:
# 			self.endResetModel()
# 			return
#
# 		if self.view_mode == "flat":
# 			for tag in self.tag_image.tags:
# 				node = ImageTagModel.Node(tag, self.root)
# 				self.root.children.append(node)
# 		else:
# 			for tag in self.tag_image.tags:
# 				parts = tag.split(":", 1)
# 				if len(parts) == 2:
# 					cat, sub = parts
# 					cat_node = next((c for c in self.root.children if c.name == cat), None)
# 					if not cat_node:
# 						cat_node = ImageTagModel.Node(cat, self.root)
# 						self.root.children.append(cat_node)
# 					cat_node.children.append(ImageTagModel.Node(sub, cat_node))
# 				else:
# 					self.root.children.append(ImageTagModel.Node(tag, self.root))
# 		self.endResetModel()
#
#
# 	def setImage(self, image: TagImage):
# 		self.tag_image = image
#
# 	def columnCount(self, parent=...):
# 		return super().columnCount(parent)
#
# 	def data(self, index, role=...):
# 		return super().data(index, role)
#
# 	def index(self, row, column, parent=...):
# 		return super().index(row, column, parent)
#
# 	def rowCount(self, parent=...):
# 		return super().rowCount(parent)
#
# 	def parent(self):
# 		return super().parent()
#
# 	class Node:
# 		def __init__(self, name: str, parent: "ImageTagModel.Node" = None):
# 			self.name = name
# 			self.parent = parent
# 			self.children: list[ImageTagModel.Node] = []
