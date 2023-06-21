# PBOKit
# Copyright 2023 Superxpdude
# PBO File Format
# https://community.bistudio.com/wiki/PBO_File_Format
import array
from datetime import datetime
import functools
import hashlib
import io
import struct

__all__ = ["PBO", "PackedFile"]

HEADER_FORMAT = "<4s4L"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def read_asciiz(stream: io.BufferedIOBase) -> str | None:
	"""Reads an ASCIIZ string from a buffered IO stream

	Parameters
	----------
	stream : io.BufferedIOBase
		File as bytes, or in-memory bytes buffer

	Returns
	-------
	str | None
		Decoded ASCIIZ string
	"""
	byteStr = b""
	for block in iter(functools.partial(stream.read, 1), b""):
		if block == b"\x00":
			break
		else:
			byteStr += block

	result = byteStr.decode()
	return result if len(result) > 0 else None


def reverse_bytes(b: bytes) -> bytes:
	"""Reverses a collection of bytes

	Parameters
	----------
	b : bytes
		Input bytes to reverse

	Returns
	-------
	bytes
		Reversed bytes
	"""
	a = array.array("I")
	a.frombytes(b)
	a.byteswap()
	return a.tobytes()


class InvalidChecksum(Exception):
	pass


class NoFileContent(Exception):
	pass


class PackedFile(object):
	content: bytes | None

	def __init__(self, fileName: str, timeStamp: int, size: int):
		self.fileName = fileName
		self.timeStamp = datetime.fromtimestamp(timeStamp)
		self.size = size

	def __repr__(self) -> str:
		return self.fileName

	def __str__(self) -> str:
		return self.fileName

	def _read(self, stream: io.BufferedIOBase) -> None:
		"""Reads the file content from the IO stream

		Parameters
		----------
		stream : io.BufferedIOBase
			IO stream

		Returns
		-------
		None
		"""
		self.content = stream.read(self.size)

	def as_bytes(self) -> bytes:
		"""Returns the file content as bytes

		Returns
		-------
		bytes
			File content as bytes
		"""
		if self.content is None:
			raise NoFileContent
		return self.content

	def as_str(self) -> str:
		"""Returns the file content as a string

		Returns
		-------
		str
			File content as a string
		"""
		return self.as_bytes().decode()


class PBO(object):

	def __init__(
		self, headers: dict[str, str] = {}, files: list[PackedFile] = []
	):
		self.headers = headers
		self.files = files

	@classmethod
	def from_file(cls, file: str) -> "PBO":
		with open(file, "rb") as f:
			return cls._build(f)

	@classmethod
	def from_bytes(cls, b: bytes) -> "PBO":
		byteStream = io.BytesIO(b)
		return cls._build(byteStream)

	@classmethod
	def _build(cls, stream: io.BufferedIOBase) -> "PBO":
		mimeType: bytes
		originalSize: int
		offset: int
		timestamp: int
		dataSize: int
		header = True
		headers: dict[str, str] = {}
		files: list[PackedFile] = []

		# Start by reading the beginning of the PBO file
		while header:
			fileName = read_asciiz(stream)
			mimeType, originalSize, offset, timestamp, dataSize = struct.unpack(
				HEADER_FORMAT, stream.read(HEADER_SIZE)
			)
			# Fix the order of the mimeType
			mimeType = reverse_bytes(mimeType)

			if mimeType == b"Vers":
				# Header prefix block, indicates that we have header entries following
				entry = read_asciiz(stream)
				while entry is not None:
					value = read_asciiz(stream)
					assert value is not None
					headers[entry] = value
					# Read the next entry value
					entry = read_asciiz(stream)
				# Loop complete. Back to normal.

			elif fileName is None:
				# Last header entry, file contents will follow
				header = False

			else:
				# File entry
				files.append(PackedFile(fileName, timestamp, dataSize))

		# Header section complete, start reading file content
		for file in files:
			file._read(stream)

		# File content complete. Reset the stream and validate the checksum
		stream.seek(0)
		rawContent = stream.read()

		# The SHA-1 hash includes the entire file except the last 21 bytes
		fileHash = hashlib.sha1(rawContent[:-21])
		# The hash in the file occupies the last 20 bytes, with a single byte separator
		if fileHash.digest() != rawContent[-20:]:
			# If the hash doesn't match, raise an error
			raise InvalidChecksum

		return cls(headers, files)

	def _get_file_by_name(self, fileName: str) -> PackedFile | None:
		"""Searches the PBO file for a packed file matching the file name

		Parameters
		----------
		fileName : str
			File name to search for. Not case-sensitive.

		Returns
		-------
		PackedFile | None
			Packed file if found
		"""
		fileNameLower = fileName.casefold().replace("/", "\\")
		for file in self.files:
			if file.fileName.casefold() == fileNameLower:
				return file
		# If we could not find a match for the filename, return none
		return None

	def has_file(self, fileName: str) -> bool:
		"""Checks if a file exists within the PBO

		Parameters
		----------
		fileName : str
			Filename to search for

		Returns
		-------
		bool
			File exists in PBO
		"""
		return True if self._get_file_by_name(fileName) is not None else False

	def file_as_bytes(self, fileName: str) -> bytes:
		"""Retrieves the contents of a file packed into the PBO in byte form

		Parameters
		----------
		fileName : str
			Filename to read

		Returns
		-------
		bytes
			File contents
		"""
		file = self._get_file_by_name(fileName)
		if file is None:
			raise FileNotFoundError
		# File exists, return its file content
		return file.as_bytes()

	def file_as_str(self, fileName: str) -> str:
		"""Retrieves the contents of a file packed into the PBO in string form

		Parameters
		----------
		fileName : str
			Filename to read

		Returns
		-------
		str
			File contents
		"""
		return self.file_as_bytes(fileName).decode()
