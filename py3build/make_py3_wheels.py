"""Build the py3 (CPython 3.10+) wheels of the Sanner lab packages from the trees built in work/.

    python make_py3_wheels.py OUTDIR [package ...]

For each package: the built package tree (Python files, compiled extensions, data, licence files;
no C/SWIG sources or build files) is laid out in src/<pkg> next to the repository's own packaging
files, with the new version and dependencies; `python -m build --wheel` makes a pure-tagged wheel,
which is retagged for this interpreter (cpXY-cpXY-linux_x86_64) and given its manylinux tag by
auditwheel. The py37 wheels (py3-none-any, holding cpython-37m extensions) are never touched.

Run it, with the interpreter of the build env (its bin/ on PATH, for patchelf and strip), in the
folder where build_exts.sh ran, which also holds clones of MolKit2 and mglutil (branch py3), or set
PY3BUILD_ROOT to that folder.
"""
import fnmatch
import glob
import os
import re
import shutil
import subprocess
import sys
import sysconfig

HERE = os.path.abspath(os.environ.get('PY3BUILD_ROOT', os.getcwd()))
W = os.path.join(HERE, 'work', 'cp%d%d' % sys.version_info[:2])
PYTAG = 'cp%d%d' % sys.version_info[:2]
SOABI = sysconfig.get_config_var('EXT_SUFFIX')          # .cpython-312-x86_64-linux-gnu.so

NUMPY = 'numpy>=1.19'
PACKAGES = {
    # name: (repo, package dir name, built tree, version, dependencies, licence files at the repo root)
    'bhtree': ('bhtreeDIST', 'bhtree', 'bhtree/bhtree', '0.0.2', [NUMPY],
               ['LICENSE.md', 'THIRD_PARTY_NOTICES.md']),
    'prody': ('prodyDIST', 'prody', 'prody/prody', '0.0.5', [NUMPY, 'biopython', 'scipy'],
              ['LICENSE.md', 'ProDy-1.5.1-LICENSE.rst', 'Python-License.txt', 'THIRD_PARTY_NOTICES.md']),
    'mslib': ('mslibDIST', 'mslib', 'mslib/mslib', '0.0.2', [NUMPY],
              ['LICENSE.md', 'THIRD_PARTY_NOTICES.md']),
    'utpackages': ('UTpackagesDIST', 'UTpackages', 'utpkg/UTpackages', '0.0.2', [NUMPY],
                   ['GPL-2.0.txt', 'LICENSE.md', 'THIRD_PARTY_NOTICES.md', 'UTpackages_license.txt']),
    'mglutil': ('mglutil', 'mglutil', 'mglutil', '0.0.5', [NUMPY],
                ['LGPL-2.1.txt', 'LICENSE.md', 'MPL-1.1.txt', 'Python-License.txt', 'THIRD_PARTY_NOTICES.md']),
    # Open Babel 3 is not a dependency: pip users install openbabel-wheel, conda users openbabel
    'molkit2': ('MolKit2', 'MolKit2', 'MolKit2', '0.0.7',
                [NUMPY, 'biopython', 'mmtf-python', 'prody==0.0.5', 'bhtree>=0.0.2', 'mglutil>=0.0.5'],
                ['LICENSE.md', 'THIRD_PARTY_NOTICES.md']),
}
# left out of the package trees: sources, build products, VCS and editor files, packaging
SKIP_DIRS = {'.git', 'build', '__pycache__', 'packaging', 'dist', '_out'}
SKIP_FILES = ['*.c', '*.cpp', '*.cxx', '*.h', '*.hpp', '*.i', '*.i.*', '*.swg', '*.o', '*.a', '*_wrap.*',
              '*.pyc', '*.bak', '*.orig', '*.rej', '*~', '.gitignore', '.gitattributes', 'build.log',
              'setup.py', 'setup.cfg', 'version.py', 'MANIFEST', 'MANIFEST.in', 'Makefile*',
              '*.cpython-3[0-9]m-*.so']               # a py37 extension must never ride along
COMPILED = {'bhtree', 'prody', 'mslib', 'utpackages'}
STRIP = shutil.which('x86_64-conda-linux-gnu-strip') or 'strip'


def run(cmd, cwd=None):
    print('+', ' '.join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def copy_tree(src, dst):
    for d, dirs, files in os.walk(src, followlinks=True):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        rel = os.path.relpath(d, src)
        for f in files:
            if any(fnmatch.fnmatch(f, p) for p in SKIP_FILES):
                continue
            if f.endswith('.so') and not f.endswith(SOABI):
                continue                               # only this interpreter's extensions
            os.makedirs(os.path.join(dst, rel), exist_ok=True)
            shutil.copy2(os.path.join(d, f), os.path.join(dst, rel, f))
            if f.endswith('.so'):                      # no debug information in the wheel
                run([STRIP, '--strip-debug', os.path.join(dst, rel, f)])


def build(name, out):
    repo, pkg, tree, version, deps, lic = PACKAGES[name]
    repo = os.path.join(HERE, repo)
    B = os.path.join(W, 'wheelbuild', name)
    shutil.rmtree(B, ignore_errors=True)
    shutil.copytree(os.path.join(repo, 'packaging'), B)
    os.remove(os.path.join(B, 'BUILD.md'))
    dst = os.path.join(B, 'src', pkg)
    copy_tree(os.path.join(W, tree) if name in COMPILED else os.path.join(HERE, tree), dst)
    for f in lic:
        shutil.copy2(os.path.join(repo, f), os.path.join(dst, f))
    if name in COMPILED and not glob.glob(os.path.join(dst, '**', '*' + SOABI), recursive=True):
        raise SystemExit('%s: no %s extension in %s' % (name, SOABI, tree))
    p = os.path.join(B, 'pyproject.toml')
    s = open(p).read()
    s = re.sub(r'(?m)^version = ".*"$', 'version = "%s"' % version, s, count=1)
    s = re.sub(r'(?ms)^dependencies = \[.*?\n\]', 'dependencies = [\n%s\n]' % ',\n'.join('"%s"' % d for d in deps), s, count=1)
    s = re.sub(r'(?m)^requires-python = ".*"$', 'requires-python = ">=3.10"', s, count=1)
    open(p, 'w').write(s)
    dist = os.path.join(B, 'dist')
    run([sys.executable, '-m', 'build', '--wheel', '--no-isolation', '--outdir', dist, B])
    whl = glob.glob(os.path.join(dist, '*.whl'))
    assert len(whl) == 1, whl
    if name in COMPILED:
        run([sys.executable, '-m', 'wheel', 'tags', '--remove', '--python-tag', PYTAG, '--abi-tag', PYTAG,
             '--platform-tag', 'linux_x86_64', whl[0]])
        whl = glob.glob(os.path.join(dist, '*-linux_x86_64.whl'))
        run([sys.executable, '-m', 'auditwheel', 'repair', '--only-plat', '--plat', 'manylinux2014_x86_64',
             '-w', out, whl[0]])
    else:
        shutil.copy2(whl[0], out)


if __name__ == '__main__':
    out = os.path.abspath(sys.argv[1])
    os.makedirs(out, exist_ok=True)
    for n in sys.argv[2:] or list(PACKAGES):
        build(n, out)
