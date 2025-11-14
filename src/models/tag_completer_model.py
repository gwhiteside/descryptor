import os.path
import sqlite3
import sys
from enum import StrEnum, auto, Enum, IntEnum
from os import PathLike
from sqlite3 import Connection

from PyQt6.QtCore import QModelIndex, Qt, QAbstractTableModel


class TagCompleterModel(QAbstractTableModel):
	class Column(IntEnum):
		NAME = 0
		POST_COUNT = 1

	def __init__(self, db_path: str | PathLike):
		super().__init__()
		self._data: list[tuple[str, int]] = []
		self._tags_by_name_asc: list[tuple[str, int]] = []
		self._tags_by_count_asc: list[tuple[str, int]] = []
		self._row_count = 0
		self._db_path = db_path
		self._connection: Connection | None = None

		self._load_data()
		# sort() needs to be called once just to ensure everything is
		# initialized correctly. This model holds presorted data for
		# performance reasons, so sort() just assigns the corresponding
		# list for data().
		self.sort(self.Column.NAME)

	def get_max_count_len(self):
		value = max(column[1] for column in self._data)
		return len(str(value))

	def get_top_percentile_tag_len(self, percentile: int):
		tag_lengths = sorted(len(a) for a, _ in self._data)
		k_index = int(percentile / 100 * (len(tag_lengths) - 1))
		k = tag_lengths[k_index]
		return k

	def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):
		"""Can pass TagCompleterModel.Column enum values for the column parameter."""
		self.layoutAboutToBeChanged.emit()

		if column == self.Column.NAME:
			if order == Qt.SortOrder.AscendingOrder:
				self._data = self._tags_by_name_asc
			else:
				self._data = self._tags_by_name_asc[::-1]

		if column == self.Column.POST_COUNT:
			if order == Qt.SortOrder.AscendingOrder:
				self._data = self._tags_by_count_asc
			else:
				self._data = self._tags_by_count_asc[::-1]

		self._row_count = len(self._data)

		self.layoutChanged.emit()

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

			# Load tags & post count. The copy is for quickly sorting on post count.

			cursor.execute("SELECT REPLACE(name, '_', ' ') AS name, post_count FROM tags ORDER BY name ASC")
			self._tags_by_name_asc = [(row["name"], row["post_count"]) for row in cursor.fetchall()]

			cursor.execute("SELECT REPLACE(name, '_', ' ') AS name, post_count FROM tags ORDER BY post_count ASC")
			self._tags_by_count_asc = [(row["name"], row["post_count"]) for row in cursor.fetchall()]

		except sqlite3.Error as exception:
			print(f"Error querying database: {str(exception)}")

		self._connection.close()
		self._connection = None
		self._row_count = len(self._data)

	# Overrides

	def columnCount(self, parent: QModelIndex = QModelIndex()):
		return 2

	def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
		if not index.isValid() or index.row() >= self._row_count:
			return None

		if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
			name, count = self._data[index.row()]

			if index.column() == 0:
				return name
			elif index.column() == 1:
				return str(count)

		if role == Qt.ItemDataRole.TextAlignmentRole and index.column() == 0:
			return Qt.AlignmentFlag.AlignLeft

		if role == Qt.ItemDataRole.TextAlignmentRole and index.column() == 1:
			return Qt.AlignmentFlag.AlignRight

		return None

		# match role:
		# 	case Qt.ItemDataRole.DisplayRole:
		# 		data = self._data[index.row()]
		# 		name = data[0]
		# 		count = data[1]
		# 		return f"{name} ({count})"
		# 	case Qt.ItemDataRole.EditRole:
		# 		data = self._data[index.row()]
		# 		name = data[0]
		# 		count = data[1]
		# 		return name
		# 	case _:
		# 		return None

	def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
		if role != Qt.ItemDataRole.DisplayRole:
			return None

		if orientation == Qt.Orientation.Horizontal:
			return ["Tag", "Count"][section]

		return None

	def rowCount(self, parent: QModelIndex):
		return self._row_count
