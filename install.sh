#!/bin/bash

echo 'Installing CD Tray'

install -m755 cdtray.py /usr/bin/cdtray
install -m644 cdtray.desktop /usr/share/applications
mkdir -p /usr/share/cdtray
install -m644 COPYING /usr/share/cdtray
mkdir -p /usr/share/icons
install -m644 cdtray.svg /usr/share/icons
patch -Np1 -i cdtray.patch /usr/bin/cdtray
sed -i "s|\(usr/bin/env python\).*|\12|" /usr/bin/cdtray
cp lang/* -r /usr/share/locale
echo 'Install complete'
