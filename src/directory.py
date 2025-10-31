from pathlib import Path

from src.image import Image

class Directory:
	image_extensions = {
		".bmp",
		".gif",
		".jpeg",
		".jpg",
		".png",
		".tiff",
	}

	def __init__(self, directory: Path):
		self.path: Path = directory
		self.images: list[Image] = []

		self.load()

	def load(self):
		images: list[Image] = []
		for path in Path(self.path).iterdir():
			if path.is_file() and path.suffix.lower() in Directory.image_extensions:
				images.append(Image(path))

		images.sort()

		self.images = images

	def save(self):
		for image in self.images:
			if image.is_modified():
				image.save_tags()

