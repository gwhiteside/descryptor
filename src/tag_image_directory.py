from pathlib import Path

from src.tag_image import TagImage

class TagImageDirectory:
	image_extensions = {
		".bmp",
		".gif",
		".jpeg",
		".jpg",
		".png",
		".tiff",
	}

	def __init__(self, directory: Path):
		self.directory: Path = directory
		self.tag_images: list[TagImage] = []

		self.load()

	def load(self):
		tag_images: list[TagImage] = []
		for file_path in Path(self.directory).iterdir():
			if file_path.is_file() and file_path.suffix.lower() in TagImageDirectory.image_extensions:
				tag_images.append(TagImage(file_path))

		tag_images.sort()

		self.tag_images = tag_images

	def save(self):
		pass

