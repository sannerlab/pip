#!/bin/bash
# Build the compiled extensions of bhtree, prody (fork), mslib (on MSMS 1.4.5) and UTpackages for one
# Python, into a clean tree per interpreter:   build_exts.sh ENV_DIR   ->  work/cpXY/...
# Run it in a folder holding clones of bhtreeDIST, prodyDIST, mslib (the MSMS library), mslibDIST and
# UTpackagesDIST (branch py3; mslib: master), or set PY3BUILD_ROOT to that folder.
# ENV_DIR is a conda env (conda-forge) with python=3.X, "numpy>=2", swig, gxx_linux-64=12,
# gcc_linux-64=12, sysroot_linux-64=2.17, libgl-devel, libglu, patchelf, python-build (+ pip auditwheel).
set -euo pipefail
E=$(cd "$1" && pwd)
H=$(cd "${PY3BUILD_ROOT:-$PWD}" && pwd)
export PATH=$E/bin:$PATH PYTHONNOUSERSITE=1
TAG=$(python -c 'import sys; print("cp%d%d" % sys.version_info[:2])')
W=$H/work/$TAG
CC_=x86_64-conda-linux-gnu-gcc CXX_=x86_64-conda-linux-gnu-g++
mkdir -p "$W"
stage() { rm -rf "$W/$2" && mkdir -p "$W/$2" && (cd "$H/$1" && tar -c --exclude=.git .) | tar -x -C "$W/$2"; }
cbuild() { (cd "$1" && CC=$CC_ CXX=$CXX_ LDSHARED="$CC_ -shared" python setup.py build_ext --inplace > build.log 2>&1) || { tail -20 "$1/build.log"; exit 1; }; }
# libstdc++ and libgcc linked statically: the conda GCC 12 runtime is newer than manylinux2014 allows
cxxbuild() { (cd "$1" && CC=$CXX_ CXX=$CXX_ LDSHARED="$CXX_ -shared -static-libstdc++ -static-libgcc" LDCXXSHARED="$CXX_ -shared -static-libstdc++ -static-libgcc" python setup.py build_ext --inplace > build.log 2>&1) || { tail -20 "$1/build.log"; exit 1; }; }

echo "== $TAG: bhtree";   stage bhtreeDIST bhtree; cbuild "$W/bhtree"
echo "== $TAG: prody";    stage prodyDIST prody;   cbuild "$W/prody"
echo "== $TAG: MSMS 1.4.5 library"
if [ ! -f "$H/work/msmslib/x86_64Linux2/libmsms1.4.5.a" ]; then
    rm -rf "$H/work/msmslib" && mkdir -p "$H/work/msmslib" && (cd "$H/mslib" && tar -c --exclude=.git .) | tar -x -C "$H/work/msmslib"
    make -C "$H/work/msmslib/x86_64Linux2" CC=$CC_ AR=x86_64-conda-linux-gnu-ar libmsms1.4.5.a > "$H/work/msmslib/make.log" 2>&1
fi
echo "== $TAG: mslib";    stage mslibDIST mslib
(cd "$W/mslib" && MSMS_SRC=$H/work/msmslib/src/lib MSMS_LIBDIR=$H/work/msmslib/x86_64Linux2 \
    CC=$CC_ LDSHARED="$CC_ -shared" python setup.py build_ext --inplace > build.log 2>&1) || { tail -20 "$W/mslib/build.log"; exit 1; }
echo "== $TAG: UTpackages"; stage UTpackagesDIST ut
for s in UTblur UTisocontour UTmesh UTsdf UTmolderivatives UTvolrend; do cxxbuild "$W/ut/${s}DIST"; done
rm -rf "$W/utpkg" && mkdir -p "$W/utpkg" && cp -r "$W/ut/UTpackages" "$W/utpkg/"
for d in blur isocontour mesh molderivatives sdf volrend; do cp -r "$W/ut/UT${d}DIST/UT${d}" "$W/utpkg/UTpackages/"; done
find "$W" -name "*$(python -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')" -path "*/bhtree/bhtree/*" -o -name "*.so" -path "*/prody/prody/*" -o -name "*.so" -path "*/mslib/mslib/*" -o -name "*.so" -path "*/utpkg/*" | sed "s|$W/||" | sort
