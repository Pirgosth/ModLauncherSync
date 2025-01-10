from distutils.core import setup
import py2exe

setup(console=['main.py'], data_files=[
    ("", [".env"]),
], options = {'py2exe': {'bundle_files': 1, 'optimize': 2, 'compressed': True}})