#!/bin/bash

echo 'Installing CD Tray'

install -m755 cdtray.py /usr/bin/cdtray
install -m644 cdtray.desktop /usr/share/applications
mkdir -p /usr/share/cdtray
install -m644 COPYING /usr/share/cdtray
sed -i "s/lang/\/usr\/share\/locale/g" /usr/bin/cdtray
sed -i "s/COPYING/\/usr\/share\/cdtray\/COPYING/g" /usr/bin/cdtray
cp lang/* -r /usr/share/locale

echo 'Istall complete'
