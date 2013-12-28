# -*- coding: utf-8 -*-

import sublime
import sublime_plugin

import os
import os.path
import shutil
import json
import tempfile
import codecs

class LocaleCommand(sublime_plugin.ApplicationCommand):
	def run(self, **args):
		new_locale = args['locale']

		s = sublime.load_settings(setting_file())
		old_locale = locale_in_settings(s)

		# if not old_locale in all_locales():
		# 	return

		if new_locale == old_locale:
			return
		else:
			replace_menu_files_from(new_locale)
			set_current_locale(s, new_locale)
			# toggle_checked(new_locale)
			update_caption(new_locale)

	def is_checked(self):
		return False

def setting_file():
	return "Preferences.sublime-settings"

def default_package_dir():
	return os.path.join(sublime.packages_path(), 'Default')

def current_dir():
	return os.path.join(sublime.packages_path(), os.path.dirname(__file__))

def menus_dir():
	return os.path.join(current_dir(), 'menus')

def locale_dir(locale):
	return os.path.join(menus_dir(), locale)

def locale_in_settings(settings):
	return settings.get('locale', 'en')

def set_current_locale(settings, locale):
	settings.set("locale", locale)
	sublime.save_settings(setting_file())

def all_locales():
	return [ name for name in os.listdir(menus_dir()) if os.path.isdir(os.path.join(menus_dir(), name)) ]

def st_menu_files():
	return [ 'Context', 'Find in Files', 'Indentation', 'Main', 'Side Bar Mount Point', 'Side Bar', 'Syntax', 'Tab Context', 'Widget Context' ]

def replace_menu_files_from(locale):
	if not os.path.isdir(default_package_dir()):
		os.mkdir(default_package_dir())

	for m in st_menu_files():
		locale_file = os.path.join(locale_dir(locale), m + ".sublime-menu." + locale )
		if not os.path.isfile(locale_file):
			continue
		else:
			shutil.copyfile(locale_file, os.path.join(default_package_dir(), m + ".sublime-menu"))

CAPTIONS = {
	'en':    'UI Language',
	'zh_CN': u'界面语言',
	'zh_TW': u'界面語言'
}

def update_caption(locale):
	path = os.path.join(current_dir(), 'Main.sublime-menu')
	menu = read_json(path)
	menu[0]['children'][1]['caption'] = CAPTIONS[locale]
	write_json(path, menu)


def toggle_checked(locale):
	path = os.path.join(current_dir(), 'Main.sublime-menu')
	menu = read_json(path)
	locale_items = menu[0]['children'][1]['children']

	for item in locale_items:
		item['checkbox'] = False

		if item['id'] == locale:
			item['checkbox'] = True

	write_json(path, menu)

def read_json(path):
	fd = codecs.open(path, 'rb', 'utf-8')
	data = fd.read()
	deserial = json.loads(data)
	fd.close()

	return deserial

def write_json(path, data):
	serial = json.dumps(data, ensure_ascii = False, indent = 4).encode('utf-8')
	temp = tempfile.NamedTemporaryFile('wb', dir = os.path.dirname(__file__), delete = False)
	tempname = temp.name

	temp.write(serial)
	temp.close()

	shutil.move(tempname, path)

def listener():
	s = sublime.load_settings(setting_file())
	s.add_on_change('locale', update_preference)

def update_preference():
	locale = locale_in_settings(sublime.load_settings(setting_file()))
	replace_menu_files_from(locale)
	update_caption(locale)

listener()
