# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Lars Bergmann
#
# GNU GENERAL PUBLIC LICENSE
#    Version 3, 29 June 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import warnings

# PIP
# compatibility! python-systemd lib strongly depends on systemd
try:
    import systemd.journal
    use_journal = True
except ImportError:
    # logging to file is possible if desired by calling build_logger with a path
    warnings.warn('Unable to log to journal!')
    use_journal = False


def build_logger(path=None):
    # one logger to rule em' all
    LOGGER = logging.getLogger('WhosOnline')

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # handler for logging to console
    # default behaviour of the StreamHandler
    console_loghandler = logging.StreamHandler()
    console_loghandler.setLevel(logging.DEBUG)
    console_loghandler.setFormatter(formatter)
    LOGGER.addHandler(console_loghandler)

    # journal handler
    if use_journal is True:
        journal_loghandler = systemd.journal.JournalHandler()
        journal_loghandler.setLevel(logging.DEBUG)
        journal_loghandler.setFormatter(formatter)
        LOGGER.addHandler(journal_loghandler)

    # handler for logging to file
    # make this optional - normally we log to journal
    if path is not None:
        file_loghandler = logging.FileHandler(path)
        file_loghandler.setLevel(logging.DEBUG)
        file_loghandler.setFormatter(formatter)
        LOGGER.addHandler(file_loghandler)

    # loglevel for both handlers
    LOGGER.setLevel(logging.DEBUG)

    return LOGGER
