from distutils.core import setup
import py2exe
import os

setup(
    windows=[{
        'script': 'MyLocalHTTPServer.py',  # Replace with your script name
        'icon_resources': [(1, 'logo.ico')]  # Specify the icon file here
    }],
    data_files=[('',['logo.ico'])],  # Ensure icon is included in the dist folder
    options={
        'py2exe': {
            'includes': ['tkinter', 'os', 'sys'],
            'bundle_files': 1,  # Bundles everything into the exe
            'compressed': True  # Compresses the executable for a smaller size
        }
    },
    zipfile=None,  # This ensures no external .zip is created for dependencies
)
