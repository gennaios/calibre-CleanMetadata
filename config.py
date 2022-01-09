#!/usr/bin/env python
# vim:fileencoding=iso-8859-1
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2014 WS64'
__docformat__ = 'restructuredtext en'

from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit

from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/CleanMetadata) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/Clean Metadata')

# Set defaults
#prefs.defaults['hello_world_msg'] = 'Hello, World!'
#prefs.defaults['limitgerman'] = True
#prefs.defaults['ignoreseries'] = False

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QHBoxLayout()
        self.setLayout(self.l)

        self.label1 = QLabel('Limit "Cleanup German Umlauts in title" to German books:')
        self.l.addWidget(self.label1)

        self.msg1 = QLineEdit(self)
        self.msg1.setText(prefs['limitgerman'])
        self.l.addWidget(self.msg1)
        self.label.setBuddy(self.msg1)

        self.label1 = QLabel('Ignore books with existing series info in "Get series info from title":')
        self.l.addWidget(self.label1)

        self.msg2 = QLineEdit(self)
        self.msg2.setText(prefs['ignoreseries'])
        self.l.addWidget(self.msg2)
        self.label.setBuddy(self.msg2)

    def save_settings(self):
        #prefs['hello_world_msg'] = unicode(self.msg.text())
        #prefs['limitgerman'] = True
        #prefs['ignoreseries'] = False

y