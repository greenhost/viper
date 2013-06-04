from distutils.core import setup
import py2exe

opts = {'py2exe': {
           'compressed':1,  
           'dist_dir': "dist/service"
           }}

setup(service=['ovpnmon'], options=opts)