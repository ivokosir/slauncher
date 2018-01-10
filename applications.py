import configparser
import os
import re
import subprocess

class DesktopEntry:
    def __init__(self, config):
        self.hidden = any([_key_is_true(config, key) for key in ['NoDisplay', 'Hidden', 'Terminal']])
        self.name = config['Desktop Entry']['Name']
        self.exec = config['Desktop Entry']['Exec']

    def run(self):
        without_codes = re.sub("%[a-zA-Z]", "", self.exec)
        subprocess.Popen(without_codes, shell=True)


def _key_is_true(config, key):
    try:
        return config['Desktop Entry'][key] == 'true'
    except KeyError:
        return False

def _read_application(application_file):
    config = configparser.ConfigParser(interpolation=None)
    config.read(application_file)
    return DesktopEntry(config)

def _get_application_files(applications_dirs):
    for applications_dir in applications_dirs:
        for (dirpath, dirnames, filenames) in os.walk(applications_dir):
            yield from [
                os.path.join(dirpath, filename)
                for filename in filenames
                if filename.endswith('.desktop')
            ]

def list():
    home = os.environ.get('HOME', '/')
    xdg_data_home = os.environ.get('XDG_DATA_HOME', os.path.join(home, '.local', 'share'))
    xdg_data_dirs = os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':')
    xdg_data_dirs = [xdg_data_home] + xdg_data_dirs
    xdg_data_dirs = [x for x in xdg_data_dirs if x]

    applications_dirs = [os.path.join(x, 'applications') for x in xdg_data_dirs]

    application_files = _get_application_files(applications_dirs)

    applications = [_read_application(f) for f in application_files]
    applications.sort(key=lambda a: a.name)
    return [a for a in applications if not a.hidden]
