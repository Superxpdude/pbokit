# PBOkit
Fully-typed Arma 3 PBO extractor library for Python 3.10 and up.
# Usage
## Load PBOkit
```python
import pbokit
```
## Read the contents of a PBO file
```python
pbo = pbokit.PBO.from_file("pbofile.pbo")
```
## Read a PBO file from bytes
```python
pbo = pbokit.PBO.from_bytes(b"bytes_go_here")
```
## Check if a file exists in the PBO
```python
pbo = pbokit.PBO.from_file("pbofile.pbo")
pbo.has_file("description.ext")
```
## Read the contents of a file in the PBO
### Binary Files
```python
pbo = pbokit.PBO.from_file("pbofile.pbo")
pbo["loadscreen.paa"].as_bytes()
```
### Text Files
```python
pbo = pbokit.PBO.from_file("pbofile.pbo")
pbo["description.ext"].as_str()
```
## Read header values from the PBO
```python
pbo = pbokit.PBO.from_file("pbofile.pbo")
pbo.headers["prefix"]
```
