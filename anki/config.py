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

import aqt
from enum import Enum

config = None

class IrregHilightType(str, Enum):
    NONE = 'NONE'
    COLOR = 'COLOR'
    CSS = 'CSS'

def config_init():
    global config

    if config is not None:
        return

    # config not yet loaded
    config = aqt.mw.addonManager.getConfig(__name__)

    if config is None:
        # no config loaded
        config = {}

    # init defaults if missing
    defaults = [ ('conjugations', {}),
                 ('irregular_tagging', True),
                 ('irregular_tag', 'irregular'),
                 ('irregular_highlight', IrregHilightType.COLOR),
                 ('irregular_css_class', 'irregular_conjugation') ]
    for d in defaults:
        if d[0] not in config:
            config[d[0]] = d[1]

def config_write():
    aqt.mw.addonManager.writeConfig(__name__, config)

def config_get():
    return config
