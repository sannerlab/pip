# Sanner Lab pip index

A [PEP 503](https://peps.python.org/pep-0503/) pip index served by GitHub Pages at
https://sannerlab.github.io/pip/. It holds only HTML pages; each links its package files to
their download URLs in the releases of
[sannerlab/downloads](https://github.com/sannerlab/downloads/releases) (`adcp-pip-py37`).

```
python -m pip install --no-deps --index-url https://sannerlab.github.io/pip/py37/ adcp==0.0.25
```

Always use `--index-url` (not `--extra-index-url`): some names, such as `prody`, belong to
unrelated projects on PyPI.

## Adding or updating a package

```
gh release upload adcp-pip-py37 <file> -R sannerlab/downloads
gh release download adcp-pip-py37 -R sannerlab/downloads -D files/
python3 make_index.py files/
git add py37 && git commit -m "Index: <package> <version>" && git push
```
