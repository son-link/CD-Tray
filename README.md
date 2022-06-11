# CD Tray

![](https://img.shields.io/github/license/son-link/CD-Tray)
![](https://img.shields.io/github/downloads/son-link/CD-Tray/total)
![](https://img.shields.io/github/stars/son-link/CD-Tray)
![](https://img.shields.io/pypi/v/cdtray)
![](https://img.shields.io/pypi/dm/cdtray?label=downloas%20on%20PyPis)
![AUR version](https://img.shields.io/aur/version/cdtray)

[https://github.com/son-link/CD-Tray](https://github.com/son-link/CD-Tray)

![CD TRay screenshoot](screenshoot.jpg)

Play your audio CDs directly from the system tray

&copy; 2012-2013 Alfonso Saavedra "Son Link"

Under GPLv3 License

## Install

### From source code:

* Clone the repo, download the zip under Code -> Download ZIP or download the last release.
* Open a terminal and go to the project folder.
* Install the dependencies:
  * **From PIP** (with administration permissions): `pip install -r requirements.txt`
  * **Debian/Ubuntu/Mint/MX Linux**:
    * apt: `apt install python3-pyqt5 python3-gst-1.0 python3-psutil`
  * **Arch Linux/Manjaro**:
    * pacman: `python-pip python-mutagen python-pyqt5 gstreamer gst-plugins-base python-psutil`
    * If yoy use **Pipewire** install the package `gst-plugin-pipewire` 

  * Copy the icon and desktop file:
    * All users:
      * `install -m 644 bin/io.sonlink.cdtray.desktop /usr/share/applications`
  	  * `install -m 644 bin/io.sonlink.cdtray.svg /usr/share/icons/cdtray.svg`
  	* Current user:
  	  * `cp bin/io.sonlink.cdtray.desktop ~/.local/share/applications`
  	  * `cp bin/io.sonlink.cdtray.svg ~/.icons/cdtray.svg`

### From Pypi:

`pip install cdtray`

### AUR:

If you use Arch Linux, Manjaro, or other Arch Linux base distributions, you can install the official package from [AUR](https://aur.archlinux.org/packages/cdtray)

For example: `yay -S pqmusic`

### Executables:

You can download a **AppImage** for **GNU/Linux** on [releases page](https://github.com/son-link/CD-Tray/releases)

### Command line options:

* -d | --device <device>: set the device to read the CD from (usualy /dev/sr0 or /dev/cdrom)
* -f | --force : if another cdtray instance is running, kill it and start a new one
