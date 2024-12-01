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
from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtCore import QCoreApplication
from .ui.ui_conjugation_row_frame import Ui_Frame as UI_ConjugationRowFrame
from .config import *
sys.path+=["%s/korean" % os.path.dirname(__file__)]
import conjugator
import re

conjugations=[
    ("declarative present informal low", conjugator.declarative_present_informal_low),
    ("declarative present informal high", conjugator.declarative_present_informal_high),
    ("declarative present formal low", conjugator.declarative_present_formal_low),
    ("declarative present formal high", conjugator.declarative_present_formal_high),
    ("declarative past informal low", conjugator.declarative_past_informal_low),
    ("declarative past informal high", conjugator.declarative_past_informal_high),
    ("declarative past formal low", conjugator.declarative_past_formal_low),
    ("declarative past formal high", conjugator.declarative_past_formal_high),
    ("declarative future informal low", conjugator.declarative_future_informal_low),
    ("declarative future informal high", conjugator.declarative_future_informal_high),
    ("declarative future formal low", conjugator.declarative_future_formal_low),
    ("declarative future formal high", conjugator.declarative_future_formal_high),
    ("declarative future conditional informal low", conjugator.declarative_future_conditional_informal_low),
    ("declarative future conditional informal high", conjugator.declarative_future_conditional_informal_high),
    ("declarative future conditional formal low", conjugator.declarative_future_conditional_formal_low),
    ("declarative future conditional formal high", conjugator.declarative_future_conditional_formal_high),
    ("-", None),
    ("inquisitive present informal low", conjugator.inquisitive_present_informal_low),
    ("inquisitive present informal high", conjugator.inquisitive_present_informal_high),
    ("inquisitive present formal low", conjugator.inquisitive_present_formal_low),
    ("inquisitive present formal high", conjugator.inquisitive_present_formal_high),
    ("inquisitive past informal low", conjugator.inquisitive_past_informal_low),
    ("inquisitive past informal high", conjugator.inquisitive_past_informal_high),
    ("inquisitive past formal low", conjugator.inquisitive_past_formal_low),
    ("inquisitive past formal high", conjugator.inquisitive_past_formal_high),
    ("-", None),
    ("imperative present informal low", conjugator.imperative_present_informal_low),
    ("imperative present informal high", conjugator.imperative_present_informal_high),
    ("imperative present formal low", conjugator.imperative_present_formal_low),
    ("imperative present formal high", conjugator.imperative_present_formal_high),
    ("-", None),
    ("propositive present informal low", conjugator.propositive_present_informal_low),
    ("propositive present informal high", conjugator.propositive_present_informal_high),
    ("propositive present formal low", conjugator.propositive_present_formal_low),
    ("propositive present formal high", conjugator.propositive_present_formal_high),
    ("-", None),
    ("connective if", conjugator.connective_if),
    ("connective and", conjugator.connective_and)
#    ("(clear field)", lambda word: '' ) # for testing purposes only
]

class ConjugationRow(QFrame):
    def eventFilter(self, obj, ev):
        if (type(ev) == QWheelEvent):
            QCoreApplication.sendEvent(obj.parent(), ev)
            return True
        return False

    def __init__(self, field_names, parent=None, field=None, conjugation=None):
        super().__init__(parent)
        self.fr = UI_ConjugationRowFrame()
        self.fr.setupUi(self)
        # filter out mouse wheel events for the comboboxes
        self.fr.comboBox_field.installEventFilter(self)
        self.fr.comboBox_conjugation.installEventFilter(self)

        self.fr.comboBox_field.addItems(field_names)
        for c in conjugations:
            (name, fn) = c
            if (name == "-"):
                n = self.fr.comboBox_conjugation.count()
                self.fr.comboBox_conjugation.insertSeparator(n)
            else:
                self.fr.comboBox_conjugation.addItem(name, c)

        if field is not None:
            self.fr.comboBox_field.setCurrentText(field)
        else:
            self.fr.comboBox_field.setCurrentIndex(-1)

        if conjugation is not None:
            self.fr.comboBox_conjugation.setCurrentText(conjugation)
        else:
            self.fr.comboBox_conjugation.setCurrentIndex(-1)

    def is_valid(self):
        t = self.fr.comboBox_field.currentText()
        d = self.fr.comboBox_conjugation.currentText()
        return t != '' and d != ''
    def field(self):
        t = self.fr.comboBox_field.currentText()
        return t if t != '' else None
    def store_in_config(self):
        if not self.is_valid():
            return
        field = self.fr.comboBox_field.currentText()
        conj = self.fr.comboBox_conjugation.currentData()[0]
        config_get()['conjugations'][field] = conj
    def del_from_config(self):
        field = self.fr.comboBox_field.currentText()
        config = config_get()
        if field not in config['conjugations']:
            return
        del config['conjugations'][field]
    def conjugation(self):
        cb = self.fr.comboBox_conjugation
        if cb.currentText() != '':
            return cb.currentText()
        else:
            return None
    def conjugate(self, word):
        cb = self.fr.comboBox_conjugation
        if cb.currentText() != '':
            conjugator_fn = cb.currentData()[1]
            rv = conjugator_fn(word)
            rv = re.sub(r'\?$', '', rv)
            return rv;
        else:
            return None
