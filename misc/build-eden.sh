#!/bin/bash -ex

# SPDX-FileCopyrightText: Copyright 2025 Eden Emulator Project
# SPDX-License-Identifier: GPL-3.0-or-later


eval "$(./vcvarsall.sh x64)"

COMPILER="MSVC"

if [ "$COMPILER" == "MSVC" ]
then
    EXTRA_CMAKE_FLAGS+=(
        -DCMAKE_CXX_COMPILER="cl.exe"
        -DCMAKE_C_COMPILER="cl.exe"
        -DCMAKE_CXX_FLAGS="-O3"
        -DCMAKE_C_FLAGS="-O3"
    )

    BUILD_TYPE="Release"
fi

if [ "$COMPILER" == "clang" ]
then
    EXTRA_CMAKE_FLAGS+=(
        -DCMAKE_CXX_COMPILER=clang-cl
        -DCMAKE_C_COMPILER=clang-cl
        -DCMAKE_CXX_FLAGS="-O3"
        -DCMAKE_C_FLAGS="-O3"
    )

    BUILD_TYPE="Release"
fi

export WINDEPLOYQT="D:/Slow Program Files/aqt/6.9.2/msvc2022_64/bin/windeployqt.exe"

[ -z "$WINDEPLOYQT" ] && { echo "WINDEPLOYQT environment variable required."; exit 1; }

echo $EXTRA_CMAKE_FLAGS

mkdir -p build && cd build
cmake .. -G Ninja \
    -DCMAKE_BUILD_TYPE="${BUILD_TYPE:-Release}" \
	-DENABLE_QT_TRANSLATION=ON \
    -DUSE_DISCORD_PRESENCE=ON \
    -DYUZU_USE_BUNDLED_SDL2=ON \
    -DBUILD_TESTING=OFF \
    -DYUZU_TESTS=OFF \
    -DDYNARMIC_TESTS=OFF \
    -DYUZU_CMD=OFF \
    -DYUZU_ROOM_STANDALONE=OFF \
    -DYUZU_USE_QT_MULTIMEDIA=${USE_MULTIMEDIA:-false} \
    -DYUZU_USE_QT_WEB_ENGINE=${USE_WEBENGINE:-false} \
    -DYUZU_ENABLE_LTO=ON \
	-DCMAKE_EXE_LINKER_FLAGS=" /LTCG" \
    -DDYNARMIC_ENABLE_LTO=ON \
    -DYUZU_USE_BUNDLED_QT=${BUNDLE_QT:-false} \
	-DQt6_DIR="D:/Slow Program Files/aqt/6.9.2/msvc2022_64/lib/cmake/Qt6" \
	-DPython3_EXECUTABLE="C:/Users/fes/.pyenv/pyenv-win/versions/3.11.7/python.exe" \
    -DUSE_CCACHE=${CCACHE:-false}  \
    -DENABLE_UPDATE_CHECKER=${DEVEL:-true} \
    "${EXTRA_CMAKE_FLAGS[@]}" \
    "$@"

ninja

set +e
rm -f bin/*.pdb
set -e

"$WINDEPLOYQT" --release --no-compiler-runtime --no-opengl-sw --no-system-dxc-compiler --no-system-d3d-compiler --dir pkg bin/eden.exe

cp bin/* pkg
