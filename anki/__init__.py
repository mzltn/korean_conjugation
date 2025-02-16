# This file is part of korean_conjugation.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import sys
import os

import aqt
from aqt.qt import QAction, qconnect
from aqt.browser import Browser
from anki.hooks import addHook

from PyQt6.QtWidgets import QDialog, QMessageBox
from bs4 import BeautifulSoup
from enum import Enum
from .ui.ui_main_dialog import Ui_Dialog as Ui_MainDialog
from .conjugation_row import *
from .config import *

sys.path+=["%s/korean" % os.path.dirname(__file__)]
import conjugator

browser_window:Browser = None
config = None

def show_messagebox_overwrite(message):
    mbox = QMessageBox()
    mbox.setText(message)
    mbox.setIcon(QMessageBox.Icon.Warning)
    mbox.setStandardButtons(QMessageBox.StandardButton.NoAll | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.YesAll)
    return mbox.exec()
def show_messagebox_info(message):
    mbox = QMessageBox()
    mbox.setText(message)
    mbox.setIcon(QMessageBox.Icon.Information)
    mbox.exec()
def show_messagebox_warning(message):
    mbox = QMessageBox()
    mbox.setText(message)
    mbox.setIcon(QMessageBox.Icon.Warning)
    mbox.exec()
def open_main_dialog():
    main_dialog = MainDialog(browser_window)
    main_dialog.exec()
    config_write()

def on_browser_made(browser: Browser):
    global browser_window
    browser_window = browser

    menu = aqt.qt.QMenu("&Dongsa", browser)
    menu_open = QAction("Generate conjugations", browser)
    qconnect(menu_open.triggered, open_main_dialog)
    menu.addAction(menu_open)
    browser.form.menubar.addMenu(menu)

def init_dongsa():
    global config
    config_init()
    config = config_get()
    addHook("browser.setupMenus", on_browser_made)

class MainDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainDialog()
        self.ui.setupUi(self)
        self.setModal(True)

        # gather field names
        self.field_names = []
        for nid in browser_window.selectedNotes():
            note = aqt.mw.col.get_note(nid)
            self.field_names += [k for k in note.keys() if k not in self.field_names]

        self.conjugations = []

        self.ui.comboBox_src.addItems(self.field_names)

        self.ui.checkBox_tag_irregulars.setChecked(config['irregular_tagging'])

        self.ui.comboBox_hilight_irregulars.addItem('none', IrregHilightType.NONE)
        self.ui.comboBox_hilight_irregulars.addItem('color', IrregHilightType.COLOR)
        self.ui.comboBox_hilight_irregulars.addItem('CSS class', IrregHilightType.CSS)
        qconnect(self.ui.comboBox_hilight_irregulars.currentIndexChanged, self.highlight_type_changed)
        if (config['irregular_highlight'] == IrregHilightType.COLOR):
            self.ui.comboBox_hilight_irregulars.setCurrentIndex(1)
        elif (config['irregular_highlight'] == IrregHilightType.CSS):
            self.ui.comboBox_hilight_irregulars.setCurrentIndex(2)

        self.ui.lineEdit_tag_irregulars.setText(config['irregular_tag'])
        self.ui.lineEdit_css_class_irregulars.setText(config['irregular_css_class'])

        qconnect(self.ui.pushButton_generate.clicked, self.generate)
        qconnect(self.ui.pushButton_addConjug.clicked, lambda : self.add_conjugation_row(None, None))

        if len(config['conjugations']) == 0:
            self.add_conjugation_row(None, None)
        else:
            available_fields = []
            for field, conj_name in config['conjugations'].items():
                if field in self.field_names:
                    self.add_conjugation_row(field, conj_name)

    def highlight_type_changed(self):
        is_css = (self.ui.comboBox_hilight_irregulars.currentData() == IrregHilightType.CSS)
        self.ui.label_css_class_irregulars.setVisible(is_css)
        self.ui.lineEdit_css_class_irregulars.setVisible(is_css)

    def _store_current_config(self):
        config['irregular_tagging'] = self.ui.checkBox_tag_irregulars.isChecked()
        config['irregular_tag'] = self.ui.lineEdit_tag_irregulars.text()
        config['irregular_highlight'] = self.ui.comboBox_hilight_irregulars.currentData()
        config['irregular_css_class'] = self.ui.lineEdit_css_class_irregulars.text()
        for row in self.conjugations:
            row.store_in_config()

    def _gen_sanity_check(self):
        src_field = self.ui.comboBox_src.currentText()
        for row in self.conjugations:
            dst_field = row.field()
            if dst_field == src_field:
                show_messagebox_warning('destination field cannot be the same as source field (%s)' % dst_field)
                return False

        conj_valid = [c for c in self.conjugations if c.is_valid()]
        for conj_a in conj_valid:
            for conj_b in conj_valid:
                if conj_b == conj_a:
                    break
                if conj_a.field() == conj_b.field():
                    show_messagebox_warning("multiple assignments to field: \"%s\"" % conj_b.field())
                    return False
                if conj_a.conjugation() == conj_b.conjugation():
                    show_messagebox_warning("both %s and %s are conjugated to %s" % (conj_a.field(), conj_b.field(), conj_a.conjugation()))
                    return False
        return True

    def _highlight(self, word):
        opt_irregular = self.ui.comboBox_hilight_irregulars.currentData()
        if opt_irregular == IrregHilightType.COLOR:
            return '<span style="color: #ff0000">%s</span>' % word
        if opt_irregular == IrregHilightType.CSS:
            css_class = self.ui.lineEdit_css_class_irregulars.text()
            return '<span class="%s">%s</span>' % (css_class, word)
        return word

    def generate(self, par):
        if not self._gen_sanity_check():
            return

        n_notes = 0
        src_field = self.ui.comboBox_src.currentText()
        irregular_tagging_enabled = self.ui.checkBox_tag_irregulars.isChecked()
        irregular_tag = self.ui.lineEdit_tag_irregulars.text()
        overwrite_command = QMessageBox.StandardButton.No

        for nid in browser_window.selectedNotes():
            note = aqt.mw.col.get_note(nid)
            note_changed = False
            if src_field not in note:
                continue
            # we need to strip HTML tags to get reliable results
            base_word = BeautifulSoup(note[src_field], 'html.parser').get_text()
            is_irregular = (conjugator.verb_type(base_word) != u'regular verb')
            for row in self.conjugations:
                if not row.is_valid():
                    continue
                dst_field = row.field()
                if dst_field not in note:
                    continue
                conjugated = row.conjugate(base_word)
                if is_irregular:
                    conjugated = self._highlight(conjugated)

                if note[dst_field] != '' and note[dst_field] != conjugated:
                    if overwrite_command not in [QMessageBox.StandardButton.YesAll, QMessageBox.StandardButton.NoAll]:
                        overwrite_command = show_messagebox_overwrite("Field %s for \"%s\" is not empty (\"%s\"). Do you want to overwrite it?" % (dst_field, base_word, note[dst_field]))
                if note[dst_field] == '' or overwrite_command in [QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.YesAll]:
                    print('update note: "%s" %s <- "%s" (current:"%s")' % (base_word, dst_field, conjugated, note[dst_field]))
                    note[dst_field] = conjugated
                    note_changed = True
                else:
                    print('wont update note: "%s" %s (current:"%s")' % (base_word, dst_field, note[dst_field]))

            if note_changed:
                n_notes += 1
                if is_irregular and irregular_tagging_enabled:
                    note.add_tag(irregular_tag)
                aqt.mw.col.update_note(note)

        # store settings that were used for generating the conjugations
        self._store_current_config()

        browser_window.search()
        show_messagebox_info("Generated conjugates for %d notes." % n_notes)

    def del_conjugation_row(self):
        fr = self.sender().parent()
        fr.del_from_config()
        self.conjugations.remove(fr)
        fr.deleteLater()
        self.ui.verticalLayout_2.removeWidget(fr)

    def add_conjugation_row(self, field, conjugation):
        qfr = ConjugationRow(self.field_names, self.ui.scrollAreaWidgetContents, field, conjugation)
        n = self.ui.verticalLayout_2.count()
        self.ui.verticalLayout_2.insertWidget(n - 2 if n >= 2 else 0, qfr)
        qfr.fr.pushButton_delete.clicked.connect(self.del_conjugation_row)
        self.conjugations += [qfr]

init_dongsa()

