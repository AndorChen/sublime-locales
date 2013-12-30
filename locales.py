# -*- coding: utf-8 -*-

import sublime

if int(sublime.version()) > 2999:
    message = u"Locales plugin only support Sublime Text 2, do not install in Sublime Text 3 Beta."
    sublime.error_message(message)
else:
    import sublime_plugin

    import os
    import os.path
    import shutil
    import json
    import tempfile
    import codecs

    __version__   = '0.0.2'
    __author__    = 'Andor Chen'
    installed_dir = os.path.basename(os.getcwd())
    setting_file  = "Preferences.sublime-settings"

    class Locale(object):
        def __init__(self, locale):
            self.locale = locale

        def run(self):
            s = sublime.load_settings(setting_file)
            old_locale = locale_in_settings(s)

            # if not old_locale in all_locales():
            #     return

            if self.locale == old_locale:
                return
            else:
                replace_menu_files_from(self.locale)
                update_caption(self.locale)
                set_current_locale(s, self.locale)

        def is_checked(self):
            s = sublime.load_settings(setting_file)
            if locale_in_settings(s) == self.locale:
                return True
            else:
                return False

    class EnglishLocaleCommand(sublime_plugin.ApplicationCommand):
        def __init__(self):
            self.locale = Locale('en')

        def run(self):
            self.locale.run()

        def is_checked(self):
            return self.locale.is_checked()

    class SimplifiedChineseLocaleCommand(sublime_plugin.ApplicationCommand):
        def __init__(self):
            self.locale = Locale('zh_CN')

        def run(self):
            self.locale.run()

        def is_checked(self):
            return self.locale.is_checked()

    class TraditionalChineseLocaleCommand(sublime_plugin.ApplicationCommand):
        def __init__(self):
            self.locale = Locale('zh_TW')

        def run(self):
            self.locale.run()

        def is_checked(self):
            return self.locale.is_checked()

    def default_package_dir():
        return os.path.join(sublime.packages_path(), 'Default')

    def current_dir():
        return os.path.join(sublime.packages_path(), installed_dir)

    def menus_dir():
        return os.path.join(current_dir(), 'menus')

    def locale_dir(locale):
        return os.path.join(menus_dir(), locale)

    def locale_in_settings(settings):
        return settings.get('locale', 'en')

    def set_current_locale(settings, locale):
        settings.set("locale", locale)
        sublime.save_settings(setting_file)

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
        s = sublime.load_settings(setting_file)
        s.add_on_change('locale', update_preference)

    def update_preference():
        locale = locale_in_settings(sublime.load_settings(setting_file))
        replace_menu_files_from(locale)
        update_caption(locale)

    listener()
