#!/bin/bash

echo 'Installing Systray CD Player'

install -m755 scdp.py /usr/bin/scdp
install -m644 scdp.desktop /usr/share/applications
sed -i "s/lang/\/usr\/share\/locale/g" /usr/bin/scdp
cp lang/* -r /usr/share/locale

echo 'Istall complete'
