#!/usr/bin/env bash

# Remove AppDir
rm -r AppDir

# Grab AppImageTools
ARCH=$(uname -m)
wget -nc "https://raw.githubusercontent.com/TheAssassin/linuxdeploy-plugin-conda/master/linuxdeploy-plugin-conda.sh"
wget -nc "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-${ARCH}.AppImage"
wget -nc "https://github.com/AppImage/AppImageKit/releases/download/12/appimagetool-${ARCH}.AppImage"
chmod +x linuxdeploy-${ARCH}.AppImage linuxdeploy-plugin-conda.sh appimagetool-${ARCH}.AppImage

# Install App

# Set Environment
export CONDA_CHANNELS='conda-forge'
export PIP_REQUIREMENTS='pyqt5 .'
export CONDA_PACKAGES='pygobject'
install -Dm644 bin/io.sonlink.cdtray.png AppDir/usr/share/icons/cdtray.png
install -Dm644 bin/io.sonlink.cdtray.appdata.xml AppDir/usr/share/metainfo/io.sonlink.cdtray.appdata.xml
# Deploy
./linuxdeploy-x86_64.AppImage \
   --appdir AppDir \
    -i bin/io.sonlink.cdtray.png \
    -d bin/io.sonlink.cdtray.desktop \
    --plugin conda \
    --custom-apprun bin/AppRun.sh \
    --output appimage
