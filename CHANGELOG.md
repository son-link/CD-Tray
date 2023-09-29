## r3 (0.3.0 stable)
* Fixed bugs on configuration and eject functions
* Now it's posible to change from play to pause and vice versa just clicking in the icon
* Now it's posible to set the device from the command line, ideal when the device is mounted by another program (for example, by Thunar)
* Check if another istance of program is running

## r4 (0.3.1 stable):

* Fixed bug on checking if another instance of scdp is running

## r5 (0.3.5 stable):

* Added new command line parameters on 31/03/2012 at 13:23 hours

## r6 (0.4.0 stable):

* Name changed to CD Tray (thanks to proper from Desdelinux's chat and forum user)
* Added "About" dialog
* Updated english translation

## r7 (0.5.0 stable)

* Now is posible select a track from submenu
* Solved a fix in eject. Now change the actual_track variable to 1 (first track)
* Other minor changes

## r8 (0.6.0 stable)

* Create a custom icon program
* Now in tracks menu the entry for actual track is disabled
* Fix a error in check if another instance of cdtray is running
* Add debian patch (the library libc.so.6 is in another directory)
* Now show notification when start new track

## r9 (0.6.1 stable)

* Now the next and previous options are disabled if it is playing the first or last track respectively

## r10 (1.0.0 stable)

* Add audio device select option (ALSA, Pulse or OSS)
* Now on startup search the path to the libc6.so.6 lib. Is no longer necessary apply the cdtray_debian.patch patch
* Other minor changes.

## r11 (1.0.1 stable)

* Fix libc6 search. Is not necesary the absolute patch.

## 2.0 RC1

* Migrate from Python 2 and PyGTK+ to Python 3 and PyQt5
* Added notifications on change track
* Added option to search on the CDDB (Compat Disc Database) of [gnudb](https://gnudb.org/index.php) for CD data and get album name, artist and track titles.
* Update Spanish translations
