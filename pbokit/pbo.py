# PBOKit
# Copyright 2023 Superxpdude
# PBO File Format
# https://community.bistudio.com/wiki/PBO_File_Format
import functools
import io

__all__ = [
	"read_asciiz",
]


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
