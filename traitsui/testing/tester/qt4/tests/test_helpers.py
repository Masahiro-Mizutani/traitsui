#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

import unittest
from unittest import mock

from traitsui.tests._tools import (
    is_qt,
    requires_toolkit,
    ToolkitName,
)
from traitsui.testing.tester import command
from traitsui.testing.tester.exceptions import Disabled
from traitsui.testing.tester.qt4 import helpers

try:
    from pyface.qt import QtGui
except ImportError:
    if is_qt():
        raise


@requires_toolkit([ToolkitName.qt])
class TestInteractions(unittest.TestCase):

    def test_mouse_click(self):
        button = QtGui.QPushButton()
        click_slot = mock.Mock()
        button.clicked.connect(click_slot)

        helpers.mouse_click_qwidget(button, 0)

        self.assertEqual(click_slot.call_count, 1)

    def test_mouse_click_disabled(self):
        button = QtGui.QPushButton()
        button.setEnabled(False)

        click_slot = mock.Mock()
        button.clicked.connect(click_slot)

        # when
        # clicking won't fail, it just does not do anything.
        # This is consistent with the actual UI.
        helpers.mouse_click_qwidget(button, 0)

        # then
        self.assertEqual(click_slot.call_count, 0)

    def test_key_sequence(self):
        # test on different Qwidget objects
        textboxes = [QtGui.QLineEdit(), QtGui.QTextEdit()]
        for i, textbox in enumerate(textboxes):
            change_slot = mock.Mock()
            textbox.textChanged.connect(change_slot)

            # when
            helpers.key_sequence_qwidget(textbox,
                                         command.KeySequence("abc"),
                                         0)

            # then
            if i == 0:
                self.assertEqual(textbox.text(), "abc")
            else:
                self.assertEqual(textbox.toPlainText(), "abc")
            # each keystroke fires a signal
            self.assertEqual(change_slot.call_count, 3)

        # for a QLabel, one can try a key sequence and nothing will happen
        textbox = QtGui.QLabel()
        helpers.key_sequence_qwidget(textbox,
                                     command.KeySequence("abc"),
                                     0)
        self.assertEqual(textbox.text(), "")

    def test_key_sequence_textbox_with_unicode(self):
        for code in range(32, 127):
            with self.subTest(code=code, word=chr(code)):
                textbox = QtGui.QLineEdit()
                change_slot = mock.Mock()
                textbox.textChanged.connect(change_slot)

                # when
                helpers.key_sequence_textbox(
                    textbox,
                    command.KeySequence(chr(code) * 3),
                    delay=0,
                )

                # then
                self.assertEqual(textbox.text(), chr(code) * 3)
                self.assertEqual(change_slot.call_count, 3)

    def test_key_sequence_unsupported_key(self):
        textbox = QtGui.QLineEdit()

        with self.assertRaises(ValueError) as exception_context:
            # QTest does not support this character.
            helpers.key_sequence_textbox(
                textbox,
                command.KeySequence(chr(31)),
                delay=0,
            )

        self.assertIn(
            "is currently not supported.",
            str(exception_context.exception),
        )

    def test_key_sequence_backspace_character(self):
        # Qt does convert backspace character to the backspace key
        # But we disallow it for now to be consistent with wx.
        textbox = QtGui.QLineEdit()

        with self.assertRaises(ValueError) as exception_context:
            helpers.key_sequence_textbox(
                textbox,
                command.KeySequence("\b"),
                delay=0,
            )

        self.assertIn(
            "is currently not supported.",
            str(exception_context.exception),
        )

    def test_key_sequence_insert_point_qlineedit(self):
        textbox = QtGui.QLineEdit()
        textbox.setText("123")

        # when
        helpers.key_sequence_textbox(
            textbox,
            command.KeySequence("abc"),
            delay=0,
        )

        # then
        self.assertEqual(textbox.text(), "123abc")

    def test_key_sequence_insert_point_qtextedit(self):
        # The default insertion point moved to the end to be consistent
        # with QLineEdit
        textbox = QtGui.QTextEdit()
        textbox.setText("123")

        # when
        helpers.key_sequence_textbox(
            textbox,
            command.KeySequence("abc"),
            delay=0,
        )

        # then
        self.assertEqual(textbox.toPlainText(), "123abc")

    def test_key_sequence_disabled(self):
        textbox = QtGui.QLineEdit()
        textbox.setEnabled(False)

        # this will fail, because one should not be allowed to set
        # cursor on the widget to type anything
        with self.assertRaises(Disabled):
            helpers.key_sequence_qwidget(textbox,
                                         command.KeySequence("abc"),
                                         0)

    def test_key_click(self):
        textbox = QtGui.QLineEdit()
        change_slot = mock.Mock()
        textbox.editingFinished.connect(change_slot)

        # sanity check on editingFinished signal
        helpers.key_sequence_qwidget(textbox, command.KeySequence("abc"), 0)
        self.assertEqual(change_slot.call_count, 0)

        helpers.key_click_qwidget(textbox, command.KeyClick("Enter"), 0)
        self.assertEqual(change_slot.call_count, 1)

        # test on a different Qwidget object - QtGui.QTextEdit()
        textbox = QtGui.QTextEdit()
        change_slot = mock.Mock()
        # Now "Enter" should not finish editing, but instead go to next line
        textbox.textChanged.connect(change_slot)
        helpers.key_click_qwidget(textbox, command.KeyClick("Enter"), 0)
        self.assertEqual(change_slot.call_count, 1)
        self.assertEqual(textbox.toPlainText(), "\n")

        # for a QLabel, one can try a key click and nothing will happen
        textbox = QtGui.QLabel()
        helpers.key_click_qwidget(textbox, command.KeyClick("A"), 0)
        self.assertEqual(textbox.text(), "")

    def test_key_click_disabled(self):
        textbox = QtGui.QLineEdit()
        textbox.setEnabled(False)
        change_slot = mock.Mock()
        textbox.editingFinished.connect(change_slot)

        with self.assertRaises(Disabled):
            helpers.key_click_qwidget(textbox, command.KeyClick("Enter"), 0)
        self.assertEqual(change_slot.call_count, 0)
