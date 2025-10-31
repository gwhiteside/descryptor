from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem

from src.image import Image


class StyledItemDelegate(QStyledItemDelegate):
	"""Custom delegate to paint items with specific colors"""

	def __init__(self, parent=None):
		super().__init__(parent)

	def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
		super().initStyleOption(option, index)

		item = index.data(Qt.ItemDataRole.DisplayRole)
		if "red" in item:
			#option.palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("red"))
			option.backgroundBrush = QBrush(QColor(128, 0, 0, 50))
		if "blue" in item:
			option.palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("blue"))
		if "green" in item:
			option.palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("green"))
		if "brown" in item:
			option.palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("brown"))

	# def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
	#
	# 	# Get the item data
	# 	item = index.data(Qt.ItemDataRole.DisplayRole)
	#
	# 	# Check if this item should have a special color (you can customize this logic)
	# 	# For example, we'll make items with "important" tag red
	# 	if "hair" in item:
	# 		option.backgroundBrush = QBrush(QColor(255, 0, 0))  # Semi-transparent red
	# 		#option.palette.setColor(option.palette.Text, QColor(255, 0, 0))  # Red text
	#
	# 	# Call the parent paint method to render the item
	# 	super().paint(painter, option, index)