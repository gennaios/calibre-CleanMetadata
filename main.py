#!/usr/bin/env python
# vim:fileencoding=iso-8859-1
from __future__ import (unicode_literals, division, absolute_import,print_function)
import re

__license__   = 'GPL v3'
__copyright__ = '2014 WS64'
__docformat__ = 'restructuredtext en'

total_books=0

if False:
    # This is here to keep my python error checker from complaining about
    # the builtin functions that will be defined by the plugin loading system
    # You do not need this code in your plugins
    get_icons = get_resources = None

from PyQt5.Qt import Qt, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QMessageBox, QLabel, QProgressDialog, QApplication, QCheckBox
from calibre.gui2 import error_dialog, info_dialog

#from calibre_plugins.CleanMetadata.config import prefs

from builtins import str as unicode
import unicodedata as ud

def rmdiacritics(str):
    '''
    Return the base character of char, by "removing" any
    diacritics like accents or curls and strokes and the like.
    '''
    str2 = ""
    for i in range(0,len(str)):
        char = str[i]
        desc = ud.name(unicode(char))
        cutoff = desc.find(' WITH ')
        if cutoff != -1:
            desc = desc[:cutoff]
        str2 = str2 + ud.lookup(desc)
    return str2

class WS64_CleanUp(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)

        self.dic_title = {}
        self.dic_authors = {}
        self.dic_series = {}
        self.shrinked = {}
        self.anzahl = {}

        self.dic_seriesindex = {}
        self.processed_books = 0

        self.gui = gui
        self.do_user_config = do_user_config

        # The current database shown in the GUI
        # db is an instance of the class LibraryDatabase2 from database.py
        # This class has many, many methods that allow you to do a lot of
        # things.
        self.db = gui.current_db

        self.l = QGridLayout()

        self.setLayout(self.l)

        #self.label = QLabel(prefs['hello_world_msg'])
        #self.l.addWidget(self.label)

        zeile = 0
        links = 0
        rechts = 1
        voll = -1
        halb = 1
        hoehe1 = 1

        self.setWindowTitle('Clean Metadata')
        self.setWindowIcon(icon)

        self.about_button = QPushButton('About "Clean Metadata"...', self)
        self.about_button.clicked.connect(self.about)
        self.l.addWidget(self.about_button,zeile,links,hoehe1,voll,Qt.AlignHCenter)

        #self.marked_button = QPushButton('Show books with only one format in the calibre GUI', self)
        #self.marked_button.clicked.connect(self.marked)
        #self.l.addWidget(self.marked_button)

        #self.last_modified_button = QPushButton('Show most recently modified books', self)
        #self.last_modified_button.clicked.connect(self.last_modified)
        #self.l.addWidget(self.last_modified_button,1,0,1,-1)


        self.dummy = QLabel('', self)
        zeile += 1
        self.l.addWidget(self.dummy,zeile,links,hoehe1,voll)

        MarkOnly = 'Mark only'
        Execute = 'Execute'

        self.umlaut_label = QLabel('<b>Cleanup German umlauts in titles</b>', self)
        self.umlaut_label.setToolTip('"Boser Ueberfall und Duell der Daemonen" => "Boser Überfall und Duell der Dämonen"')
        zeile += 1
        self.l.addWidget(self.umlaut_label,zeile,links,hoehe1,voll,Qt.AlignHCenter)
        self.umlaut_checkbox = QCheckBox('limit to German books',self)
        zeile += 1
        self.l.addWidget(self.umlaut_checkbox,zeile,links,hoehe1,voll,Qt.AlignHCenter)
        self.umlaut_button_mark = QPushButton(MarkOnly, self)
        self.umlaut_button_mark.clicked.connect(lambda: self.process_books('umlaut','mark'))
        zeile += 1
        self.l.addWidget(self.umlaut_button_mark,zeile,links,hoehe1,halb,Qt.AlignHCenter)
        self.umlaut_button_clean = QPushButton(Execute, self)
        self.umlaut_button_clean.clicked.connect(lambda: self.process_books('umlaut','clean'))
        self.l.addWidget(self.umlaut_button_clean,zeile,rechts,hoehe1,halb,Qt.AlignHCenter)

        self.dummy2 = QLabel('', self)
        zeile += 1
        self.l.addWidget(self.dummy2,zeile,links,hoehe1,voll)

        self.titles_label = QLabel('<b>Cleanup titles</b>', self)
        self.titles_label.setToolTip('"This is a book title (German Edition)" / "This is a book title. A novel" / "This_is_a_book_title" => "This is a book title"')
        zeile += 1
        self.l.addWidget(self.titles_label,zeile,links,hoehe1,voll,Qt.AlignHCenter)
        self.titles_button_mark = QPushButton(MarkOnly, self)
        self.titles_button_mark.clicked.connect(lambda: self.process_books('titles','mark'))
        zeile += 1
        self.l.addWidget(self.titles_button_mark,zeile,links,hoehe1,halb,Qt.AlignHCenter)
        self.titles_button_clean = QPushButton(Execute, self)
        self.titles_button_clean.clicked.connect(lambda: self.process_books('titles','clean'))
        self.l.addWidget(self.titles_button_clean,zeile,rechts,hoehe1,halb,Qt.AlignHCenter)

        self.dummy3 = QLabel('', self)
        zeile += 1
        self.l.addWidget(self.dummy3,zeile,links,hoehe1,voll)

        self.series_label = QLabel('<b>Get series info from title</b>', self)
        self.series_label.setToolTip('"Harry Potter 3: The Prisoner of Azkaban" => title: "The Prisoner of Azkaban", series: "Harry Potter", series_index: 3')
        zeile += 1
        self.l.addWidget(self.series_label,zeile,links,hoehe1,voll,Qt.AlignHCenter)
        self.series_checkbox = QCheckBox('ignore books with existing series info',self)
        zeile += 1
        self.l.addWidget(self.series_checkbox,zeile,links,hoehe1,voll,Qt.AlignHCenter)
        self.series_button_mark = QPushButton(MarkOnly, self)
        self.series_button_mark.clicked.connect(lambda: self.process_books('series','mark'))
        zeile += 1
        self.l.addWidget(self.series_button_mark,zeile,links,hoehe1,halb,Qt.AlignHCenter)
        self.series_button_clean = QPushButton(Execute, self)
        self.series_button_clean.clicked.connect(lambda: self.process_books('series','clean'))
        self.l.addWidget(self.series_button_clean,zeile,rechts,hoehe1,halb,Qt.AlignHCenter)

        self.dummy4 = QLabel('', self)
        zeile += 1
        self.l.addWidget(self.dummy4,zeile,links,hoehe1,voll)

        self.author_label = QLabel('<b>Cleanup authors</b>', self)
        self.author_label.setToolTip('"Lastname, A B.C. Firstname; Anotherlastname, Anotherfirstname" => 1: "A. B. C. Firstname Lastname", 2: "Anotherfirstname Anotherlastname"')
        zeile += 1
        self.l.addWidget(self.author_label,zeile,links,hoehe1,voll,Qt.AlignHCenter)
        self.author_button_mark = QPushButton(MarkOnly, self)
        self.author_button_mark.clicked.connect(lambda: self.process_books('authors','mark'))
        zeile += 1
        self.l.addWidget(self.author_button_mark,zeile,links,hoehe1,halb,Qt.AlignHCenter)
        self.author_button_clean = QPushButton(Execute, self)
        self.author_button_clean.clicked.connect(lambda: self.process_books('authors','clean'))
        self.l.addWidget(self.author_button_clean,zeile,rechts,hoehe1,halb,Qt.AlignHCenter)

        self.dummy5 = QLabel('', self)
        zeile += 1
        self.l.addWidget(self.dummy5,zeile,links,hoehe1,voll)

        self.authortitle_label = QLabel('<b>Swap author and title if title matches an existing author</b>', self)
        self.authortitle_label.setToolTip('title: "Stephen King", author: "Cujo" => title: "Cujo", author: "Stephen King" *if* there is already one other book in your library with author "Stephen King"')
        zeile += 1
        self.l.addWidget(self.authortitle_label,zeile,links,hoehe1,voll,Qt.AlignHCenter)
        self.authortitle_button_mark = QPushButton(MarkOnly, self)
        self.authortitle_button_mark.clicked.connect(lambda: self.process_books('authortitle','mark'))
        zeile += 1
        self.l.addWidget(self.authortitle_button_mark,zeile,links,hoehe1,halb,Qt.AlignHCenter)
        self.authortitle_button_clean = QPushButton(Execute, self)
        self.authortitle_button_clean.clicked.connect(lambda: self.process_books('authortitle','clean'))
        self.l.addWidget(self.authortitle_button_clean,zeile,rechts,hoehe1,halb,Qt.AlignHCenter)

        self.dummy5 = QLabel('', self)
        zeile += 1
        self.l.addWidget(self.dummy5,zeile,links,hoehe1,voll)

        self.dubauthor_label = QLabel('<b>Find duplicate author candidates</b>', self)
        self.dubauthor_label.setToolTip('Will try to find books by authors like "D. Ray Koontz" or "Dean Koontz" if you have marked a book by "Dean R. Koontz"')
        zeile += 1
        self.l.addWidget(self.dubauthor_label,zeile,links,hoehe1,voll,Qt.AlignHCenter)
        self.dubauthor_button_mark = QPushButton(MarkOnly, self)
        self.dubauthor_button_mark.clicked.connect(lambda: self.process_books('dubauthor','mark'))
        zeile += 1
        self.l.addWidget(self.dubauthor_button_mark,zeile,links,hoehe1,halb,Qt.AlignHCenter)
        self.dubauthor_checkbox = QCheckBox('just use first letter of firstname',self)
        zeile += 1
        self.l.addWidget(self.dubauthor_checkbox,zeile,links,hoehe1,voll,Qt.AlignHCenter)

        #self.test_button = QPushButton('Test', self)
        #self.test_button.clicked.connect(self.test)
        #zeile += 1
        #self.l.addWidget(self.test_button,zeile,links,hoehe1,voll)

        #self.conf_button = QPushButton('Configure this plugin', self)
        #self.conf_button.clicked.connect(self.config)
        #self.l.addWidget(self.conf_button)

        self.resize(self.sizeHint())
        self.matched_ids = []

    def about(self):
        # Get the about text from a file inside the plugin zip file
        # The get_resources function is a builtin function defined for all your
        # plugin code. It loads files from the plugin zip file. It returns
        # the bytes from the specified file.
        #
        # Note that if you are loading more than one file, for performance, you
        # should pass a list of names to get_resources. In this case,
        # get_resources will return a dictionary mapping names to bytes. Names that
        # are not found in the zip file will not be in the returned dictionary.
        text = get_resources('about.txt')
        QMessageBox.about(self, 'About "WS64 CleanUp"',
                text.decode('iso-8859-1'))

    def marked(self):
        ''' Show books with only one format '''
        fmt_idx = self.db.FIELD_MAP['formats']
        matched_ids = set()
        for record in self.db.data.iterall():
            # Iterate over all records
            fmts = record[fmt_idx]
            # fmts is either None or a comma separated list of formats
            if fmts and ',' not in fmts:
                matched_ids.add(record[0])
        # Mark the records with the matching ids
        self.db.set_marked_ids(matched_ids)

        # Tell the GUI to search for all marked records
        self.gui.search.setEditText('marked:true')
        self.gui.search.do_search()

    def view(self):
        ''' View the most recently added book '''
        most_recent = most_recent_id = None
        timestamp_idx = self.db.FIELD_MAP['last_modified']

        for record in self.db.data:
            # Iterate over all currently showing records
            timestamp = record[timestamp_idx]
            if most_recent is None or timestamp > most_recent:
                most_recent = timestamp
                most_recent_id = record[0]

        if most_recent_id is not None:
            # Get the row number of the id as shown in the GUI
            row_number = self.db.row(most_recent_id)
            # Get a reference to the View plugin
            view_plugin = self.gui.iactions['View']
            # Ask the view plugin to launch the viewer for row_number
            view_plugin._view_books([row_number])

        # Tell the GUI to search for all marked records
        self.gui.search.setEditText('marked:true')
        self.gui.search.do_search()


    def process_umlaut(self,book_id):
        if self.umlaut_checkbox.isChecked():
            raus = True
            for l in self.db.new_api.field_for('languages', book_id):
                if l == 'deu' or l == 'German':
                    raus = None
            if raus:
                return None

        str = self.db.new_api.field_for('title', book_id)
        str2 = str

        str=re.sub('ae','ä',str)
        str=re.sub('oe','ö',str)
        str=re.sub('ue','ü',str)
        str=re.sub('Ae','Ä',str)
        str=re.sub('Oe','Ö',str)
        str=re.sub('Ue','Ü',str)

        if str != str2:

            str=re.sub('aü','aue',str)
            str=re.sub('eü','eue',str)
            str=re.sub('xü','xue',str)
            str=re.sub('ä( |$|,|!|;)','ae\g<1>',str)
            str=re.sub('ö( |$|,|!|;)','oe\g<1>',str)
            str=re.sub('ü( |$|,|!|;)','ue\g<1>',str)
            str=re.sub('(q|Q)ü','\g<1>ue',str)
            str=re.sub('(g|d|G|D)ös','\g<1>oes',str)
            str=re.sub('(bl|Bl|tr|Tr)üs','\g<1>ues',str)
            str=re.sub('äl( |i|$|,|!|;)','ael\g<1>',str)
            str=re.sub('Öt','Oet',str)
            str=re.sub('(P|p)ö','\g<1>oe',str)
            str=re.sub('Höne','Hoene',str)
            str=re.sub('(d|D)ü(l|t)','\g<1>ue\g<2>',str)
            str=re.sub('(z|Z)ünde','\g<1>uende',str)
            str=re.sub('tül','tuel',str)
            str=re.sub('ürill','uerill',str)
            str=re.sub('ürit','uerit',str)
            str=re.sub('ütte','uette',str)
            str=re.sub('(z|Z)ürs','\g<1>uers',str)
            str=re.sub('Färie','Faerie',str)
            str=re.sub('Göthe','Goethe',str)
            str=re.sub('Jös','Joes',str)
            str=re.sub('Menue','Menü',str)
            str=re.sub('Mästr','Maestr',str)
            str=re.sub('Bullerbue','Bullerbü',str)
            str=re.sub('ichäla','ichaela',str)
            str=re.sub('mpoer','mpör',str)
            str=re.sub('güla','guela',str)
            str=re.sub('mäl','mael',str)
            str=re.sub('üva','ueva',str)
            str=re.sub('erös','eroes',str)
            str=re.sub('igül','iguel',str)
            str=re.sub('amül','amuel',str)
            str=re.sub('Cär','Caer',str)
            str=re.sub('Nathän','Nathaen',str)
            str=re.sub('Lemül','Lemuel',str)
            str=re.sub('Präsep','Praesep',str)
            str=re.sub('hüs','hues',str)
            str=re.sub('Grülf','Gruelf',str)
            str=re.sub('hüs','hues',str)
            str=re.sub('Dädalus','Daedalus',str)
            str=re.sub('Rüpp','Ruepp',str)
            str=re.sub('Blübelle','Bluebelle',str)
            str=re.sub('Säculum','Saeculum',str)
            str=re.sub('Cadfäls','Cadfaels',str)
            str=re.sub('eagues','eagüs',str)

            str=re.sub('huette','hütte',str)
            str=re.sub('huete','hüte',str)

            print (str)

            if str != str2:
                self.dic_title[book_id] = str
                self.processed_books += 1
                self.matched_ids.append(book_id)

    def process_titles(self,book_id,title):

        if not title:
            str = self.db.new_api.field_for('title', book_id)
        else:
            str = title

        aut = list(self.db.new_api.field_for('authors', book_id))

        str2 = str

        str=re.sub('  ',' ',str)

        regex = re.search('^(.*), (eine?|der|die|das|the|a)$',str,re.IGNORECASE)
        if regex:
            str = regex.group(2)+" "+regex.group(1)

        str=re.sub(r'(?i)-ok$','',str)
        str=re.sub(r'(?i)-neu$','',str)
        str=re.sub('_',' ',str)
        str=re.sub('-[0-9][0-9][.][0-9][0-9][.][0-9][0-9]','',str)
        wegdamit = '((eine?|a) )?(v[0-9]|eine biographie|Piper Taschenbuch|Psycho-Thriller|insel taschenbuch|Erweiterte Ausgabe|fantasy|science fiction|kurzgeschichten|sammelband|ebook|heyne fliegt|ebook special|taschenbuch|sonderausgabe|gratis|umsonst|knaur hc|knaur tb|german edition|gesammelte werke|suhrkamp taschenbuch|Stories|Roman|Historischer Kriminalroman|Erotischer Roman|Liebesroman|Erzählungen|Erzaehlungen|Aktionspreis|historischer Roman|Novel|Novelle|Kriminalroman|Thriller|Psychothriller|gesamtausgabe|Australien-Roman|txt|pdf|docx?|epub|mobi|zip|docx?|epub|ebup|mobi|zip|rtf)'
        str=re.sub(r'(?i)( ?[:|/.] ?| - ?)'+wegdamit+'$','',str)
        str=re.sub(r'(?i) ?\('+wegdamit+'\)$','',str)
        str=re.sub(r'(?i) ?\['+wegdamit+'\]$','',str)
        str=re.sub(r'(?i) ?{'+wegdamit+'}$','',str)

        regex = re.search('^(.*), (eine?|der|die|das|the|a)$',str,re.IGNORECASE)
        if regex:
            str = regex.group(2)+" "+regex.group(1)

        str=re.sub('-$','',str)

        regex = re.search('^(.*) ?- ?'+aut[0]+'$',str,re.IGNORECASE)
        if regex:
            str = regex.group(1)

        regex = re.search('^'+aut[0]+': ?(.*)$',str,re.IGNORECASE)
        if regex:
            str = regex.group(1)

        regex = re.search('^(.*) ?- ?'+aut[0]+' ?- ?(.*)$',str,re.IGNORECASE)
        if regex:
            str = regex.group(1)+" - "+regex.group(2)

        regex = re.search('^' + aut[0]+' (.*)$',str,re.IGNORECASE)
        if regex:
            str = regex.group(1)

        str=str[0].upper()+str[1:]

        str=re.sub(r'(?i)^FreeBooks? ','',str)

        str=re.sub('  ',' ',str)


        print (str)
        if str != str2:
            self.dic_title[book_id] = str
            if not title:
                self.processed_books += 1
                self.matched_ids.append(book_id)
            self.process_titles(book_id,str)

    def process_series(self,book_id):
        if not self.series_checkbox.isChecked() or str(self.db.new_api.field_for('series_index', book_id))=="None":
            regex = re.search('([^0-9-]+) #?([0-9]+) ?(-|:) (.*)',self.db.new_api.field_for('title', book_id))
            if regex:
                self.dic_title[book_id] = regex.group(4)
                reg1 = regex.group(1)
                reg2 = regex.group(2)
                self.dic_series[book_id] = re.sub('(Vol|Bd|Band|Volume)[.]? ?','',reg1)
                self.dic_seriesindex[book_id] = reg2
                self.processed_books += 1
                self.matched_ids.append(book_id)

    def process_authors(self,book_id):
        authors = list(self.db.new_api.field_for('authors',book_id))
        actual_author = 0
        number_authors = len(authors)
        change = None

        while actual_author < number_authors:
            print('Vorher: '+authors[actual_author])
            regex = re.search('([^;]*); ?(.*)',authors[actual_author])
            while regex:
                authors[actual_author] = regex.group(1)
                authors.append(regex.group(2))
                regex = re.search('([^;]*); ?(.*)',authors[actual_author])
                change = True

            regex = re.search('(.*), *(.*)',authors[actual_author]) # Nachname, Vorname => Vorname Nachname
            if regex:
                str = regex.group(2).upper()
                if str !="JR" and str !="SR" and str !="JR." and str !="SR.":
                    authors[actual_author] = regex.group(2) + ' ' + regex.group(1)
                    change = True

            regex = re.search('(^|.*[ ])(.)[ ](.*)',authors[actual_author]) # S King => S. King
            while regex:
                authors[actual_author] = regex.group(1) + regex.group(2) + '. ' + regex.group(3)
                regex = re.search('(^|.*[ ])(.)[ ](.*)',authors[actual_author])
                change = True

            regex = re.search('(.*[.])([A-ZÄÖÜ].*)',authors[actual_author]) # S.King => S. King
            while regex:
                authors[actual_author] = regex.group(1) + ' ' + regex.group(2)
                regex = re.search('(.*[.])([A-ZÄÖÜ].*)',authors[actual_author])
                change = True

            number_authors = len(authors)

            print('Nachher: '+authors[actual_author])
            actual_author += 1

        if change:
            self.dic_authors[book_id] = tuple(authors)
            self.processed_books += 1
            self.matched_ids.append(book_id)

    def process_authortitle(self,book_id):
        aut = self.db.new_api.field_for('authors', book_id)
        if len(aut) == 1: #Author field has just one entry
            tit = self.db.new_api.field_for('title', book_id)
            if len(self.db.new_api.search('author:"='+aut[0]+'"'))==1 and tit != aut[0]: #it exists only one author with that name and title and author are different
                if self.db.new_api.search('author:"='+tit+'"'):
                    self.dic_authors[book_id] = tit
                    self.dic_title[book_id] = aut[0]
                    self.processed_books += 1
                    self.matched_ids.append(book_id)
                regex = re.search('(.*), *(.*)',tit) # Nachname, Vorname => Vorname Nachname
                if regex:
                    str = regex.group(2).upper()
                    if str !="JR" and str !="SR" and str !="JR." and str !="SR.":
                        tit = regex.group(2) + ' ' + regex.group(1)
                        if self.db.new_api.search('author:"='+tit+'"'):
                            self.dic_authors[book_id] = tit
                            self.dic_title[book_id] = aut[0]
                            self.processed_books += 1
                            self.matched_ids.append(book_id)

    def remove_letters(self,str):
        doppelt = 'bcdefghklmnpqrstvwxzjy '
                                                                                      #Dr. Ésteban Secondname Umläeutter!
        aut_shrink = str.lower().strip()                                              #dr. ésteban sedondname umläeutter!
        aut_shrink = re.sub('-',' ',aut_shrink)
        aut_shrink = re.sub('(^| )(dr|med|prof|der|die|das|the|a)\.? ','',aut_shrink) #ésteban sedondname umläeutter!
        aut_shrink = rmdiacritics(aut_shrink)                                         #esteban sedondname umlaeutter!

        aut_shrink = re.sub('[^a-z ]','',aut_shrink).strip()                          #esteban sedondname umlaeutter

        if re.search(' ',aut_shrink):
            if self.dubauthor_checkbox.isChecked():
                regex = re.search('^([^ ])(.*?)([^ ]+)$',aut_shrink)
            else:
                regex = re.search('^([^ ]+)(.*?)([^ ]+)$',aut_shrink)
            aut_shrink = regex.group(1)+' '+regex.group(3)                            #esteban umlaeutter


        #aut_shrink = re.sub('[eajy]','',aut_shrink)                                 #stbn mlttr
        for j in range(0,len(doppelt)):
            aut_shrink = re.sub(doppelt[j]+doppelt[j],doppelt[j],aut_shrink)           #stbn mltr
            aut_shrink = re.sub(doppelt[j]+doppelt[j],doppelt[j],aut_shrink)
            aut_shrink = re.sub(doppelt[j]+doppelt[j],doppelt[j],aut_shrink)
        if len(aut_shrink)==0:
            aut_shrink='-'
        return aut_shrink

    def process_dubauthor(self,book_id):
        author_ids = self.db.new_api.field_ids_for('authors', book_id)
        adata = self.db.new_api.author_data()
        aut_list = [adata[i] for i in adata]

        if len(self.shrinked)==0:
            for rec in aut_list:
                aut = rec['name']
                aut_shrink = self.remove_letters(aut)
                self.shrinked[aut] = aut_shrink
                try:
                    self.anzahl[aut_shrink] += 1
                except:
                    self.anzahl[aut_shrink] = 1

        authors = list(self.db.new_api.field_for('authors',book_id))
        actual_author = 0
        number_authors = len(authors)
        change = None

        while actual_author < number_authors:
            aut = self.remove_letters(authors[actual_author])
            if self.anzahl[aut]>1:
                str = ''
                for val in self.shrinked:
                    if aut == self.shrinked[val]:
                        str = str + ' or author:"='+val+'"'
                str = str[4:]
                for id in self.db.new_api.search(str):
                    self.processed_books += 1
                    self.matched_ids.append(id)
            actual_author += 1

        #info_dialog(self, 'Updated books',str,show=True)


    def process_books(self,action,type):
        '''
        Set the metadata in the files in the selected book's record to
        match the current metadata in the database.
        '''

        # Get currently selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Cannot update metadata','No books selected', show=True)
        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        processed_book = 0
        progress = QProgressDialog("Processing books","Stop" , 0,len(ids) ,self)
        progress.setWindowTitle("Clean Metadata")
        progress.show()
        progress.setValue(0)
        actual_book = 0
        raus = None

        self.dic_title = {}
        self.dic_authors = {}
        self.dic_series = {}
        self.dic_seriesindex = {}

        self.shrinked = {}
        self.anzahl = {}

        self.processed_books = 0

        self.matched_ids = []

        for book_id in ids:
            actual_book += 1
            progress.setValue(actual_book)
            QApplication.processEvents()

            if progress.wasCanceled():
                raus = True

            if not raus:
                if action == 'authors':
                    self.process_authors(book_id)
                elif action == 'series':
                    self.process_series(book_id)
                elif action == 'titles':
                    self.process_titles(book_id,None)
                elif action == 'umlaut':
                    self.process_umlaut(book_id)
                elif action == 'authortitle':
                    self.process_authortitle(book_id)
                elif action == 'dubauthor':
                    self.process_dubauthor(book_id)

        if type == 'clean':
            if len(self.dic_title)>0:
                self.db.new_api.set_field('title', self.dic_title)
            if len(self.dic_authors)>0:
                self.db.new_api.set_field('authors', self.dic_authors)
            if len(self.dic_series)>0:
                self.db.new_api.set_field('series', self.dic_series)
            if len(self.dic_seriesindex)>0:
                self.db.new_api.set_field('series_index', self.dic_seriesindex)
            info_dialog(self, 'Updated books','%d book(s) (out of %d) updated'%(self.processed_books,len(ids)),show=True)
            #self.gui.search.do_search()
        elif type == 'mark':
            if self.matched_ids:
                self.db.set_marked_ids(self.matched_ids)
                self.gui.search.setEditText('marked:true')
                self.gui.search.do_search()
            else:
                info_dialog(self, 'Updated books ('+action+')','No matching books found!',show=True)

        progress.close()

    def config(self):
        self.do_user_config(parent=self)
        # Apply the changes
        self.label.setText(prefs['hello_world_msg'])


    def test(self):
        erg = self.db.new_api.search('author:"=Grertertimm"')
        info_dialog(self, 'Updated books',str(len(erg)),show=True)