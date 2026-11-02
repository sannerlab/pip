#!/usr/bin/env python3
"""Write a PEP 503 "simple" pip index for the files of one GitHub release.

    python3 make_index.py <files-dir> [--index py37] [--release adcp-pip-py37]

<files-dir> holds the release's files (to compute their sha256). The index pages link each
file to its download URL on github.com/sannerlab/downloads, so this repo holds only HTML.
To add or update a package: upload the file to the release, download the release's files
(gh release download adcp-pip-py37 -R sannerlab/downloads -D files/), rerun, commit, push.
"""
import argparse, hashlib, html, re
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("files")
p.add_argument("--index", default="py37")
p.add_argument("--release", default="adcp-pip-py37")
a = p.parse_args()
base = f"https://github.com/sannerlab/downloads/releases/download/{a.release}/"

projects = {}
for f in sorted(Path(a.files).iterdir()):
    m = re.match(r"(.+?)-\d[^-]*(-py\d.*\.whl|\.tar\.gz|\.zip)$", f.name)
    if not m:
        raise SystemExit(f"not a package file: {f.name}")
    name = re.sub(r"[-_.]+", "-", m.group(1)).lower()  # PEP 503 normalised name
    projects.setdefault(name, []).append(
        (f.name, hashlib.sha256(f.read_bytes()).hexdigest()))

def page(title, body):
    return (f'<!DOCTYPE html>\n<html><head><meta name="pypi:repository-version" content="1.0">'
            f"<title>{html.escape(title)}</title></head>\n<body>\n{body}</body></html>\n")

out = Path(a.index)
out.mkdir(exist_ok=True)
(out / "index.html").write_text(page(f"Sanner Lab pip index ({a.index})", "".join(
    f'<a href="{n}/">{n}</a><br>\n' for n in sorted(projects))))
for n, files in projects.items():
    (out / n).mkdir(exist_ok=True)
    (out / n / "index.html").write_text(page(f"Links for {n}", "".join(
        f'<a href="{base}{fn}#sha256={h}">{html.escape(fn)}</a><br>\n' for fn, h in files)))
print(f"{a.index}: {len(projects)} projects, {sum(map(len, projects.values()))} files")
