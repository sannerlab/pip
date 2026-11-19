# Sanner Lab pip index

A [PEP 503](https://peps.python.org/pep-0503/) pip index served by GitHub Pages at
https://sannerlab.github.io/pip/. It holds only HTML pages; each links its package files to
their download URLs in the releases of
[sannerlab/downloads](https://github.com/sannerlab/downloads/releases).

- **`py37/`** (release `adcp-pip-py37`): the Python 3.7 packages of ADCP 1.1 and ADFRsuite.
  Their wheels are tagged `py3-none-any` but hold `cpython-37m` extensions: they work on Python 3.7 only.

  ```
  python -m pip install --no-deps --index-url https://sannerlab.github.io/pip/py37/ adcp==0.0.25.post1
  ```

- **`py3/`** (release `adcp-pip-py3`): bhtree, prody (the lab's fork of ProDy 1.5.1), mslib (MSMS),
  utpackages, mglutil and molkit2 for CPython 3.10 to 3.13 on Linux x86_64 (manylinux2014). They are
  what WEWoS's Molecules library and isocontouring need on current Python. Their dependencies from
  PyPI are installed first (Open Babel as `openbabel-wheel`), then the packages themselves:

  ```
  python -m pip install numpy biopython scipy mmtf-python openbabel-wheel
  python -m pip install --no-deps --index-url https://sannerlab.github.io/pip/py3/ \
      molkit2==0.0.7 prody==0.0.5 bhtree==0.0.2 mglutil==0.0.5 mslib==0.0.2 utpackages==0.0.2
  ```

The two indexes never share a file: the versions on `py3/` are newer than those on `py37/` (molkit2
0.0.7 and 0.0.6, for example), and the `py37/` files stay as they are.

Always use `--index-url` (not `--extra-index-url`), with exact versions: some names, such as `prody` and `mslib`, belong to
unrelated projects on PyPI.

## Licenses

Each package carries its license: the Sannerlab MIT-like Source-Available License
(https://sannerlab.github.io/software/license.html), customized for the package, with a
`THIRD_PARTY_NOTICES.md` for the third-party code it includes. The exceptions: the ADCP docking
engine (in `adcp`) is under the GNU LGPL v2.0, and MSMS (`mslib`, `mglkey`) is closed source under
the MSMS License. The `.post1` releases of November 18, 2026 are the original packages with these
license files; the earlier files are still listed so that exact pins keep working. The source
archives (`.tar.gz`) stay in the release but are no longer listed.

## Adding or updating a package

```
gh release upload adcp-pip-py37 <file> -R sannerlab/downloads
gh release download adcp-pip-py37 -R sannerlab/downloads -D files/
python3 make_index.py files/
git add py37 && git commit -m "Index: <package> <version>" && git push
```

For the `py3` index: the release is `adcp-pip-py3`, and `python3 make_index.py files/ --index py3
--release adcp-pip-py3`, then `git add py3`.

## Building the py3 wheels

`py3build/build_exts.sh` builds the compiled extensions for one Python (one conda-forge env per
Python, with GCC 12 and the glibc 2.17 sysroot), and `py3build/make_py3_wheels.py` makes the wheels
(manylinux2014 tags from auditwheel). They run in a folder holding the `py3` branches of
bhtreeDIST, prodyDIST, mslibDIST, UTpackagesDIST, MolKit2 and mglutil, and the MSMS library
(sannerlab/mslib). Each repository's `packaging/BUILD.md` lists what changed for Python 3.10+.
