# PBOKit
# Copyright 2023 Superxpdude
# PBO File Format
# https://community.bistudio.com/wiki/PBO_File_Format
import array
from datetime import datetime
import functools
import io
import struct
from typing import Self

__all__ = ["read_asciiz", "PBO", "PBOFile"]

HEADER_FORMAT = "4sLLLL"
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


class PBOFile(object):
	content: bytes

	def __init__(self, fileName: str, timeStamp: int, size: int):
		self.fileName = fileName
		self.timeStamp = datetime.fromtimestamp(timeStamp)
		self.size = size

	def __repr__(self) -> str:
		return self.fileName

	def __str__(self) -> str:
		return self.fileName


class PBO(object):

	def __init__(
		self, headers: dict[str, str] = {}, files: list[PBOFile] = []
	):
		self.headers = headers
		self.files = files

	@classmethod
	def from_file(cls, file: str) -> Self:

		with open(file, "rb") as f:
			return cls._build(f)

	@classmethod
	def _build(cls, stream: io.BufferedIOBase) -> Self:
		mimeType: bytes
		originalSize: int
		offset: int
		timestamp: int
		dataSize: int
		header = True
		headers: dict[str, str] = {}
		files = []
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
				files.append(PBOFile(fileName, timestamp, dataSize))

		return cls(headers, files)
