from PyQt6.QtCore import QAbstractListModel, Qt, QModelIndex, QThreadPool
from PyQt6.QtGui import QColor, QFont, QIcon

from settings.config import Config, Setting
from models.image import Image
from models.directory import Directory
from gui.thumbnail_task import ThumbnailLoader, ThumbnailTask


class DirectoryImageModel(QAbstractListModel):
	def __init__(self, directory: Directory | None = None):
		super().__init__()
		self.directory: Directory | None = None
		self.changed_background = QColor(Config.read(Setting.ModifiedColor))
		self.changed_font = QFont(None, -1, -1, True)
		self.loading_icon = QIcon.fromTheme(QIcon.ThemeIcon.ImageLoading)

		self.loader = ThumbnailLoader()
		self.loader.thumbnail_ready.connect(self.on_thumbnail_ready)

		self.setDirectory(directory)

	def data(self, index: QModelIndex = QModelIndex(), role: int = Qt.ItemDataRole.DisplayRole):
		image: Image = self.directory.images[index.row()]

		match role:
			case Qt.ItemDataRole.BackgroundRole:
				return self.changed_background if image.is_modified() else None
			case Qt.ItemDataRole.DecorationRole:
				return self.load_async_thumbnail(image)
			case Qt.ItemDataRole.DisplayRole:
				return image.path.name
			case Qt.ItemDataRole.FontRole:
				return self.changed_font if image.is_modified() else None
			#case Qt.ItemDataRole.SizeHintRole:
			#	return QSize(200, 200)
			case Qt.ItemDataRole.UserRole:
				return image
			case _:
				return None

	def rowCount(self, parent: QModelIndex = QModelIndex()):
		return len(self.directory.images) if self.directory else 0

	def load_async_thumbnail(self, image: Image):
		if image.thumbnail is None:
			image.thumbnail = self.loading_icon
			task = ThumbnailTask(image, self.loader)
			QThreadPool.globalInstance().start(task, 0)
		return image.thumbnail

	def on_thumbnail_ready(self, image: Image):
		row = self.directory.images.index(image)
		index = self.index(row, 0)
		self.dataChanged.emit(index, index, [Qt.ItemDataRole.DecorationRole])

	def on_image_tags_modified(self, image: Image):
		"""
		Handles tag modification signal from tag editor to ensure immediate
		updates on the selector view.
		"""
		row = self.directory.images.index(image)
		index = self.index(row)
		self.dataChanged.emit(index, index)

	def save(self):
		self.directory.save()

	def setDirectory(self, directory: Directory):
		self.layoutAboutToBeChanged.emit()
		self.directory = directory
		self.layoutChanged.emit()
