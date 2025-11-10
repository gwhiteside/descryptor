from dataclasses import dataclass
from enum import Enum

from PyQt6.QtCore import QSettings, QByteArray

APP_NAME = "descryptor"


@dataclass(frozen=True)
class Entry:
	key: str
	default: object

class Setting(Enum):
	RestoreLayout = Entry("restore_layout", True)

	LayoutGeometry = Entry("Layout/geometry", QByteArray())
	LayoutState = Entry("Layout/state", QByteArray())
	UnifiedTagDock = Entry("Layout/unified_tag_dock", False)

	RecentDirectories = Entry("Recent/directories", [])

	ModifiedColor = Entry("Colors/modified_color", "#CC3333")
	IndexMatchColor = Entry("Colors/index_match_color", "#33CC33")

class Config:
	_manager = QSettings(APP_NAME, APP_NAME)

	@staticmethod
	def contains(entry: Setting) -> bool:
		return Config._manager.contains(entry.value.key)

	@staticmethod
	def initialize():
		for setting in Setting:
			key = setting.value.key
			if not Config._manager.contains(key):
				Config._manager.setValue(key, setting.value.default)

	@staticmethod
	def read(entry: Setting | str):
		if isinstance(entry, Setting):
			value = Config._manager.value(entry.value.key, entry.value.default)
			type_of = type(entry.value.default)
			if type_of is bool:
				return Config.str_to_bool(value)
		else:
			value = Config._manager.value(entry, None)
			type_of = str

		return value

	@staticmethod
	def reset(entry: Setting):
		Config._manager.remove(entry.value.key)

	@staticmethod
	def str_to_bool(string: str):
		mapping = {
			"true": True,
			"false": False,
			"1": True,
			"0": False,
			"yes": True,
			"no": False,

			"none": False,
		}

		value = mapping.get(string.lower())
		if value is not None:
			return value
		else:
			return False

	@staticmethod
	def write(entry: Setting | str, value):
		if isinstance(entry, Setting):
			Config._manager.setValue(entry.value.key, value)
		else:
			Config._manager.setValue(entry, value)