## distutils_symlink_enabler

You can give symlink to package_data.

## caveats

Only build_py and sdist are supported. bdist is not supported yet~

## demo

https://github.com/cielavenir/package_data_symlink

try `python -m pip install .` on it.

## quick usage (for now)

cf https://pybind11.readthedocs.io/en/stable/compiling.html#copy-manually

- setup.py

```
import sys
sys.path.append(abspath(dirname(__file__)))

from setuptools import setup
import distutils_symlink_enabler
```

- MANIFEST.in

```
include distutils_symlink_enabler.py
```
