from PyQt6.QtCore import QAbstractListModel, Qt, QModelIndex
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtWidgets import QApplication

from src.tag_image import TagImage
from src.tag_image_directory import TagImageDirectory


class TagImageListModel(QAbstractListModel):
	def __init__(self, tag_image_directory: TagImageDirectory | None = None):
		super().__init__()
		self.tag_image_directory = None
		self.changed_background = QBrush(QColor(255, 0, 0, 50))
		self.changed_font = QFont(None, -1, -1, True)

		self.setDirectory(tag_image_directory)

	def data(self, index: QModelIndex, role: int):
		tag_image = self.tag_image_directory.tag_images[index.row()]
		match role:
			case Qt.ItemDataRole.BackgroundRole:
				return self.changed_background if tag_image.modified else None
			case Qt.ItemDataRole.DecorationRole:
				return tag_image.thumbnail
			case Qt.ItemDataRole.DisplayRole:
				return tag_image.path.name
			case Qt.ItemDataRole.FontRole:
				return self.changed_font if tag_image.modified else None
			case Qt.ItemDataRole.UserRole:
				return tag_image
			case _:
				return None

	def rowCount(self, index: QModelIndex):
		return len(self.tag_image_directory.tag_images)

	def tagsModified(self, item: TagImage):
		"""
		Handles tag modification signal from tag editor to ensure immediate
		updates on the selector view.
		"""
		row = self.tag_image_directory.tag_images.index(item)
		index = self.index(row)
		self.dataChanged.emit(index, index)

	def setDirectory(self, tag_image_directory: TagImageDirectory):
		self.tag_image_directory = tag_image_directory
