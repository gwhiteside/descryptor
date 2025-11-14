import time


class Stopwatch():
	"""It's just more convenient than typing it out."""
	_start_time: float = 0.0
	_stop_time: float = 0.0
	_elapsed_time: float = 0.0

	@classmethod
	def print(cls):
		print(f"Elapsed time: {cls._elapsed_time:.6f} seconds")

	@classmethod
	def start(cls):
		cls._start_time = time.perf_counter()

	@classmethod
	def stop(cls):
		cls._stop_time = time.perf_counter()
		cls._elapsed_time = cls._stop_time - cls._start_time
		cls.print()