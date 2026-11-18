# Sanner Lab pip index

A [PEP 503](https://peps.python.org/pep-0503/) pip index served by GitHub Pages at
https://sannerlab.github.io/pip/. It holds only HTML pages; each links its package files to
their download URLs in the releases of
[sannerlab/downloads](https://github.com/sannerlab/downloads/releases) (`adcp-pip-py37`).

```
python -m pip install --no-deps --index-url https://sannerlab.github.io/pip/py37/ adcp==0.0.25.post1
```

Always use `--index-url` (not `--extra-index-url`): some names, such as `prody`, belong to
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
