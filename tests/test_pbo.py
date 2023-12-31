import pbokit
import pytest
from pbokit.pbo import InvalidChecksum, NoFileContent


@pytest.fixture
def pbofile() -> pbokit.PBO:
	return pbokit.PBO.from_file("tests/test.pbo")


@pytest.fixture
def pboBytes() -> bytes:
	file = open("tests/test.pbo", "rb")
	return file.read()


def test_read_pbo(pbofile):
	assert pbofile is not None


def test_read_bytes():
	with open("tests/test.pbo", "rb") as file:
		pbofile = pbokit.PBO.from_bytes(file.read())


@pytest.mark.parametrize(
	"filename, exists", [
		pytest.param("file1.txt", True, id="File 1"),
		pytest.param("file2.txt", True, id="File 2"),
		pytest.param("python.png", True, id="Image"),
		pytest.param("myfolder/file3.txt", True, id="File in subfolder"),
		pytest.param("file3.txt", False, id="Missing 1"),
		pytest.param("myfolder/file1.txt", False, id="Missing 2"),
		pytest.param("python", False, id="Missing 3"),
	]
)
def test_file_exists(pbofile: pbokit.PBO, filename: str, exists: bool):
	assert pbofile.has_file(filename) == exists
	assert (filename.casefold() in pbofile.filenames()) == exists


def test_file_no_content():
	file = pbokit.PackedFile("testfile.txt", 1, 1)
	with pytest.raises(NoFileContent):
		file.as_bytes()


@pytest.mark.parametrize(
	"filename, data", [
		pytest.param("file1.txt", "Hello World", id="File 1"),
		pytest.param(
			"file2.txt", "A\r\nB\r\nC\r\nD\r\nE\r\nF\r\nG", id="File 2"
		),
		pytest.param("myfolder/file3.txt", "PBOkit", id="File in subfolder"),
	]
)
def test_read_textfile(pbofile: pbokit.PBO, filename: str, data: str):
	assert pbofile[filename].as_str() == data


def test_read_invalid_name(pbofile: pbokit.PBO):
	with pytest.raises(TypeError):
		pbofile[1]  #type: ignore


@pytest.mark.parametrize(
	"filename, data", [
		pytest.param(
			"python.png",
			open("tests/python.png", "rb").read(),
			id="Python Logo"
		),
	]
)
def test_read_image(pbofile: pbokit.PBO, filename: str, data: bytes):
	assert pbofile[filename].as_bytes() == data


def test_fail_checksum():
	with pytest.raises(InvalidChecksum):
		pbokit.PBO.from_file("tests/test_bad_checksum.pbo")


@pytest.mark.parametrize(
	"header, value", [
		pytest.param("prefix", "pbokit\\test", id="Prefix"),
		pytest.param("version", "1.2.3", id="Version"),
	]
)
def test_headers(pbofile: pbokit.PBO, header: str, value: str):
	assert pbofile.headers[header] == value


def test_fail_write(pbofile: pbokit.PBO):
	with pytest.raises(NotImplementedError):
		pbofile["file4.txt"] = pbokit.PackedFile("file4.txt", 1000, 20)


def test_fail_delete(pbofile: pbokit.PBO):
	with pytest.raises(NotImplementedError):
		del pbofile["file1.txt"]
