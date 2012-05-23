#!/usr/bin/env python
# -*- coding: utf-8 -*-

# CD Tray: Play your Audio CDs from systray
# (c) 2012 Alfonso Saavedra "Son Link"
# http://sonlinkblog.blogspot.com.es/p/scripts.html
# Under GPLv3 License

import gobject, gtk
import gettext
import gst

from ConfigParser import ConfigParser
from os import environ
from os.path import isfile
from commands import getoutput
from ctypes import CDLL
from optparse import OptionParser

configfile = environ['HOME']+'/.cdtray'

APP = 'cdtray'
gettext.textdomain (APP)
gettext.bindtextdomain (APP, 'lang')
_ = gettext.gettext
gettext.install(APP, 'lang', unicode=1)


class CDTRAY():
	"""
	Init the program
	"""
	
	def __init__(self):		
		self.actual_track = 1
		
		self.status = -1
		self.device = ''
		# -1 -> No hace nada, 0 Stop, 1 play, 2 pause
		
		self.cfg = ConfigParser()
		self.readconfig()
		
		self.statusicon = gtk.StatusIcon()
		
		self.statusicon.set_from_stock(gtk.STOCK_CDROM)
		self.statusicon.connect("popup-menu", self.show_menu)
		self.statusicon.connect('activate', self.play)
		
		self.menu= gtk.Menu()
		
		# Play
		self.play_button = gtk.ImageMenuItem(stock_id=gtk.STOCK_MEDIA_PLAY)
		self.play_button.connect('activate', self.play)
		self.menu.append(self.play_button)
		
		# Next
		about = gtk.ImageMenuItem(stock_id=gtk.STOCK_MEDIA_NEXT)
		about.connect('activate', self.next)
		self.menu.append(about)
		
		# Previous
		config = gtk.ImageMenuItem(stock_id=gtk.STOCK_MEDIA_PREVIOUS)
		config.connect('activate', self.prev)
		self.menu.append(config)
		
		# Selection track
		self.tracks_menu = gtk.Menu()
		self.importm = gtk.MenuItem(label=_('Jump to'))
		self.importm.set_submenu(self.tracks_menu)
		self.menu.append(self.importm)
				
		stop = gtk.ImageMenuItem(stock_id=gtk.STOCK_MEDIA_STOP)
		stop.connect('activate', self.stop)
		self.menu.append(stop)
		
		eject = gtk.MenuItem(label=_('Eject'))
		eject.connect('activate', self.eject)
		self.menu.append(eject)
		
		sep = gtk.SeparatorMenuItem()
		self.menu.append(sep)
		
		config = gtk.ImageMenuItem(stock_id=gtk.STOCK_PREFERENCES)
		config.connect('activate', self.configure)
		self.menu.append(config)
		
		about = gtk.ImageMenuItem(stock_id=gtk.STOCK_ABOUT)
		about.connect('activate', self.about)
		self.menu.append(about)
		
		salir = gtk.ImageMenuItem(stock_id=gtk.STOCK_QUIT)
		salir.connect('activate', self.quit)
		self.menu.append(salir)

		if self.autostart == 1:
			self.play()
		
	def show_menu(self, icon, button, time):
		"""
		Show the menu
		"""
		
		self.menu.show_all()
		self.menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)
					
	def play(self, *args):
		"""
		Change the state to play or pause
		"""
		
		if self.status == 1:
			self.pipeline.set_state(gst.STATE_PAUSED)
			self.status = 2
			
		elif self.status == 2:
			self.pipeline.set_state(gst.STATE_PLAYING)
			self.status = 1
		
		else:
			self.create_pipeline()			
			self.pipeline.set_state(gst.STATE_PLAYING)
			self.status = 1
		
	def prev(self, w, *args):
		"""
		Change to previous track
		"""
		
		if self.actual_track > 1:
			self.actual_track -= 1
			self.pipeline.set_state(gst.STATE_READY)
			self.pipeline.get_by_name("cdda").set_property("track", self.actual_track)
			self.pipeline.set_state(gst.STATE_PLAYING)
			self.update_info()
		
	def stop(self, *args):
		"""
		Stop
		"""
		try:
			self.pipeline.set_state(gst.STATE_NULL)
		except:
			pass
			
		self.status = 0
	
	def next(self, w, *args):
		"""
		Change to next track
		"""
		if self.actual_track < self.file_tags['track-count']:
			self.actual_track += 1
		
			self.pipeline.set_state(gst.STATE_READY)
			self.pipeline.get_by_name("cdda").set_property("track", self.actual_track)
			self.pipeline.set_state(gst.STATE_PLAYING)
			self.update_info()
		else:
			self.stop()
			self.actual_track = 1
		
	def eject(self, w, *args):
		"""
		Eject the CD
		"""
		
		self.stop()
		self.actual_track = 1
		getoutput('eject '+ self.device)
		
	def create_pipeline(self):
		"""
		Create the pipelino for playing
		"""
		
		cdsrc = 'cdparanoiasrc device=%s track=%i name=cdda ! audioconvert ! volume name=volume ! alsasink' % (self.device, self.actual_track)
		self.pipeline = gst.parse_launch(cdsrc)
		
		bus = self.pipeline.get_bus()
		
		bus.add_signal_watch()
		
		bus.connect("message::tag", self.bus_message_tag)
		bus.connect("message::error", self.bus_message_error)
		bus.connect("message::eos", self.next)
			
	def bus_message_error(self, bus, message, txt):
		e, d = message.parse_error()
		self.statusicon.set_tooltip_text("ERROR: "+ str(e))
	
	def bus_message_tag(self, bus, message):
		
		"""Esta es la función encargada de recoger los datos del bus de Gstreamer, principalmente los tags de los ficheros de audio"""
		self.file_tags = {}
		
		taglist = message.parse_tag()
		
		for key in taglist.keys():
			try:
				self.file_tags[key] = taglist[key]
			except:
				return False
		
		self.update_info()
		self.update_jt_menu()
		
	def update_info(self):
		"""
		Show info on icon tooltip
		"""
		if self.actual_track < 10:
			track = '0'+str(self.actual_track)
		else:
			track = str(self.actual_track)
			
		if self.file_tags['track-count'] < 10:
			total_tracks = '0'+str(self.file_tags['track-count'])
		else:
			total_tracks = str(self.file_tags['track-count'])
		
		info_text = _('Track #actual_track of #total_tracks')
		info_text = info_text.replace('#actual_track', track)
		info_text = info_text.replace('#total_tracks', total_tracks)
		self.statusicon.set_tooltip_text(info_text)
		
	def update_jt_menu(self):
		"""
		Update the Jump To submenu
		"""
		#self.menu.clear()
		self.tracks_menu = gtk.Menu()
		self.importm.set_submenu(self.tracks_menu)
		for i in range(1, self.file_tags['track-count']+1):
			buf = "Track %d" % i
			menu_items = gtk.MenuItem(_("Track %d") % i)
			self.tracks_menu.append(menu_items)
			menu_items.connect("activate", self.change_track, i)
						
	def change_track(self, widget, track):
		self.actual_track = track
		self.pipeline.set_state(gst.STATE_READY)
		self.pipeline.get_by_name("cdda").set_property("track", self.actual_track)
		self.pipeline.set_state(gst.STATE_PLAYING)
		self.update_info()
		
	def readconfig(self):
		"""
		Read the configuration
		"""
		if not isfile(configfile):
			f = open(configfile, 'w')
			f.write("[cdtray]\ndevice=/dev/sr0\nautostart=0")
			f.close()
			
		self.cfg.read([configfile])
		
		if options.device:
			self.device = options.device
		else:
			self.device = self.cfg.get('cdtray', 'device')
			
		self.autostart = int(self.cfg.get('cdtray', 'autostart'))
		
	def configure(self, w):
		
		"""
		Show dialog for configure the program
		"""
		configwin = gtk.Dialog(_("Configure CD Tray"), buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
		
		def __saveconfig(w, res):
			"""
			Save the new configuration
			"""
			# Destroy the configuratión dialog
			
			if res == gtk.RESPONSE_ACCEPT:
				# If press Accept, save the new configuration
				cfg = ConfigParser()
				cfg.read([configfile])
				cfg.set('cdtray', 'device', self.device_entry.get_text())
				
				if self.autostart_check.get_active():
					cfg.set('cdtray', 'autostart', 1)
				else:
					cfg.set('cdtray', 'autostart', 0)
					
				f = open(configfile, "w")
				cfg.write(f)
				f.close()
				self.stop()
				self.actual_track = 1
				self.status = -1
				self.device = self.device_entry.get_text()
				self.play()
				
			w.destroy()
		
		hbox1 = gtk.HBox()
		configwin.vbox.add(hbox1)
		
		label = gtk.Label(str=_('Set CD Device'))
		label.set_alignment(0, 0)
		label.set_padding(5, 5)
		hbox1.pack_start(label, False, False, 0)
		
		self.device_entry = gtk.Entry()
		self.device_entry.set_text(self.device)
		hbox1.pack_start(self.device_entry, False, False, 0)
		
		hbox1 = gtk.HBox()
		configwin.vbox.add(hbox1)
		
		self.autostart_check = gtk.CheckButton(label=_('autostart at boot'))
		if self.autostart == 1:
			self.autostart_check.set_active(True)
			
		configwin.vbox.add(self.autostart_check)
		
		configwin.connect("response", __saveconfig)
		configwin.show_all()
			
	def about(self, w):
		# The about dialog
		
		info = gtk.AboutDialog()
		info.set_name('CD Tray')
		info.set_version('r6 (0.4.0 stable)')
		f = open('COPYING', 'r')
		info.set_license(f.read())
		f.close()
		info.set_comments(_('Special Thanks:\nTo the Desde linux users for supporting me with their ideas\nTo Desdelinux\'s user proper for helping me with the name of the program\nAnd for all of you for downloading and using this program'))
		info.set_website('http://sonlinkblog.blogspot.com/p/pacsyu.html')
		info.set_website_label(_("Proyect page on my blog (Only in spanish)"))
		info.set_translator_credits('English: Alfonso Saavedra "Son Link"\nAurosZx')
		def close(w, res):
			w.hide()
		info.connect("response", close)
		info.run()

	def quit(self, w):
		"""
		Exit from program
		"""
		self.stop()
		exit()
	
if __name__ == '__main__':

	usage = "Usage: %prog [options]"
	parser = OptionParser(usage=usage, version='r7 (0.5.0 stable)')
	parser.add_option("-d", "--device", dest="device",
	action="store", metavar="DEVICE", type='str', help=_("Set CD device"))
	parser.add_option("-f", "--force", action="store_true", dest="force", default=False, help=_("Force kill another cdtray instance"))
		
	(options, args) = parser.parse_args()

	process = getoutput('ps -A')
	# Check is exist another PacSyu instace
	if not 'cdtray' in process:
		libc = CDLL('/lib/libc.so.6')
		libc.prctl (15, 'scdp', 0, 0, 0)
		CDTRAY()
		gtk.main()
		
	else:
		if options.force:
			kill = getoutput('killall cdtray')
			libc = CDLL('/lib/libc.so.6')
			libc.prctl (15, 'cdtray', 0, 0, 0)
			CDTRAY()
			gtk.main()
		else:
			warning = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_OK, message_format=_("Error!"))
			warning.format_secondary_text(_("There is another cdtray instance running. If the program didn't close correctly, kill cdtray process"))
			def close(w, res):
				w.destroy()
				exit(1)
			warning.connect("response", close)
			warning.run()
