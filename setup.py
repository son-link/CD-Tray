from setuptools import setup

setup(
    name="cdtray",
    version="2.0.rc1",
    description="Play your audio CDs directly from the system tray",
    author="Alfonso Saavedra 'Son Link'",
    author_email='sonlink.dourden@gmail.com',
    license="GPL 3.0",
    url="https://github.com/son-link/CD-Tray",
    scripts=['bin/cdtray'],
    packages=['CDTray'],
    package_dir={'CDTray': 'CDTray'},
    package_data={'CDTray': ['*', 'locales/*.qm', 'LICENSE']},
    include_package_data=True,
    exclude_package_data={
        '/': [
            '*.sh',
            'build/',
            'dist/',
            'icons/luv-icon-theme',
            'cdtray.py',
            '*.backup',
            'package',
            'debian',
            '.github'
            '.vscode'
            'aur',
        ]
    },
    download_url='https://github.com/son-link/CD-Tray/archive/refs/tags/v.2.0.rc1.tar.gz',
    keywords=['music', 'audio', 'player'],
    install_requires=[
        'pyqt5',
        'python-gst',
        'psutil',
        'PyGobject'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'Topic :: Multimedia :: Sound/Audio :: CD Audio',
        'Topic :: Multimedia :: Sound/Audio :: CD Audio :: CD Playing',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent'
    ],
)
