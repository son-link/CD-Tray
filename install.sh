#!/bin/bash

echo 'Installing CD Tray'

install -m755 cdtray.py /usr/bin/cdtray
install -m644 cdtray.desktop /usr/share/applications
mkdir -p /usr/share/cdtray
install -m644 COPYING /usr/share/cdtray
sed -i "s/lang/\/usr\/share\/locale/g" /usr/bin/cdtray
sed -i "s/COPYING/\/usr\/share\/cdtray\/COPYING/g" /usr/bin/cdtray
echo 'You use Debian/Ubuntu/Linux Mint on other deribated distributions? [y/N]'
read debian
if [ $debian = 'y' ] || [ $debian = 'Y' ]; then
	patch -Np1 -i cdtray_debian.patch /usr/bin/cdtray
else
	patch -Np1 -i cdtray.patch /usr/bin/cdtray
fi
cp lang/* -r /usr/share/locale

echo 'Install complete'
