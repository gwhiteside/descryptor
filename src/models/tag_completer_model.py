import os.path
import sqlite3
import time
from os import PathLike
from sqlite3 import Connection

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt


class TagCompleterModel(QAbstractListModel):
	def __init__(self, db_path: str | PathLike):
		super().__init__()
		self._tags = []
		self._tag_count = 0
		self._db_path = db_path
		self._connection: Connection | None = None
		self._load_data()

	def _connect_database(self):
		if not os.path.exists(self._db_path):
			print ("Error: database not found")
			return False

		try:
			self._connection = sqlite3.connect(self._db_path)
			self._connection.row_factory = sqlite3.Row
			return True
		except sqlite3.Error as exception:
			print(f"Error connecting to database: {str(exception)}")
			return False

	def _load_data(self):
		if not self._connect_database():
			return

		try:
			cursor = self._connection.cursor()
			cursor.execute("SELECT REPLACE(name, '_', ' ') AS name FROM tags ORDER BY name ASC")
			self.layoutAboutToBeChanged.emit()
			self._tags = [row["name"] for row in cursor.fetchall()]
			self.layoutChanged.emit()
		except sqlite3.Error as exception:
			print(f"Error querying database: {str(exception)}")

		self._connection.close()
		self._connection = None
		self._tag_count = len(self._tags)

	# Overrides

	def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
		if not index.isValid() or index.row() >= self._tag_count:
			return None

		match role:
			case Qt.ItemDataRole.DisplayRole:
				return self._tags[index.row()]
			case Qt.ItemDataRole.EditRole:
				return self._tags[index.row()]
			case _:
				return None

	def rowCount(self, parent: QModelIndex = QModelIndex()):
		return self._tag_count
