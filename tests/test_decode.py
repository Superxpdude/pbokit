import io
import pbokit
import pytest


@pytest.mark.parametrize(
	"b, s", [
		pytest.param(b"", None, id="Empty"),
		pytest.param(b"Arma", "Arma", id="Basic 1"),
		pytest.param(b"Altis", "Altis", id="Basic 2"),
		pytest.param(b"Stratis", "Stratis", id="Basic 3"),
		pytest.param(b"Malden\x001234", "Malden", id="ASCIIZ 1"),
		pytest.param(
			b"Livonia\x001234\x005678\x009999", "Livonia", id="ASCIIZ 2"
		),
	]
)
def test_decode_asciiz(b: bytes, s: str | None):
	byteStream = io.BytesIO(b)
	assert pbokit.read_asciiz(byteStream) == s
