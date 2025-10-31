from PyQt6.QtCore import QAbstractListModel, Qt, QModelIndex
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtWidgets import QApplication

from src.image import Image
from src.directory import Directory



class DirectoryImageModel(QAbstractListModel):
	def __init__(self, directory: Directory | None = None):
		super().__init__()
		self.directory = None
		self.changed_background = QBrush(QColor(255, 0, 0, 50))
		self.changed_font = QFont(None, -1, -1, True)

		self.setDirectory(directory)

	def data(self, index: QModelIndex, role: int):
		image: Image = self.directory.images[index.row()]

		match role:
			case Qt.ItemDataRole.BackgroundRole:
				return self.changed_background if image.is_modified() else None
			case Qt.ItemDataRole.DecorationRole:
				return image.thumbnail
			case Qt.ItemDataRole.DisplayRole:
				return image.path.name
			case Qt.ItemDataRole.FontRole:
				return self.changed_font if image.is_modified() else None
			case Qt.ItemDataRole.UserRole:
				return image
			case _:
				return None

	def rowCount(self, parent: QModelIndex = QModelIndex()):
		return len(self.directory.images) if self.directory else 0

	def tagsModified(self, item: Image):
		"""
		Handles tag modification signal from tag editor to ensure immediate
		updates on the selector view.
		"""
		row = self.directory.images.index(item)
		index = self.index(row)
		self.dataChanged.emit(index, index)

	def save(self):
		self.directory.save()

	def setDirectory(self, directory: Directory):
		self.layoutAboutToBeChanged.emit()
		self.directory = directory
		self.layoutChanged.emit()
