# ------------------------------------------------------------------------------
#
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Pietro Berkes
#  Date:   Feb 2012
#
# ------------------------------------------------------------------------------

"""
Test cases for the UI object.
"""

import unittest

from pyface.api import GUI
from traits.api import Property
from traits.has_traits import HasTraits, HasStrictTraits
from traits.trait_types import Str, Int
import traitsui
from traitsui.api import Group, View
from traitsui.item import Item, spring

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.tests._tools import (
    count_calls,
    create_ui,
    is_qt,
    is_wx,
    process_cascade_events,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)
from traitsui.toolkit import toolkit, toolkit_object


class FooDialog(HasTraits):
    """Test dialog that does nothing useful."""

    my_int = Int(2)
    my_str = Str("hallo")

    traits_view = View(Item("my_int"), Item("my_str"), buttons=["OK"])


class DisallowNewTraits(HasStrictTraits):
    """ Make sure no extra traits are added.
    """

    x = Int(10)

    traits_view = View(Item("x"), spring)


class MaybeInvalidTrait(HasTraits):

    name = Str()

    name_is_invalid = Property(depends_on="name")

    traits_view = View(
        Item("name", invalid="name_is_invalid")
    )

    def _get_name_is_invalid(self):
        return len(self.name) < 10


class TestUI(unittest.TestCase):

    @requires_toolkit([ToolkitName.wx])
    def test_reset_with_destroy_wx(self):
        # Characterization test:
        # UI.reset(destroy=True) destroys all ui children of the top control

        foo = FooDialog()
        with create_ui(foo) as ui:

            ui.reset(destroy=True)

            # the top control is still there
            self.assertIsNotNone(ui.control)
            # but its children are gone
            self.assertEqual(len(ui.control.GetChildren()), 0)

    @requires_toolkit([ToolkitName.qt])
    def test_reset_with_destroy_qt(self):
        # Characterization test:
        # UI.reset(destroy=True) destroys all ui children of the top control

        from pyface import qt

        foo = FooDialog()
        with create_ui(foo) as ui:

            # decorate children's `deleteLater` function to check that it is
            # called on `reset`. check only with the editor parts (only widgets
            # are scheduled.
            # See traitsui.qt4.toolkit.GUIToolkit.destroy_children)
            for c in ui.control.children():
                c.deleteLater = count_calls(c.deleteLater)

            ui.reset(destroy=True)

            # the top control is still there
            self.assertIsNotNone(ui.control)

            # but its children are scheduled for removal
            for c in ui.control.children():
                if isinstance(c, qt.QtGui.QWidget):
                    self.assertEqual(c.deleteLater._n_calls, 1)

    @requires_toolkit([ToolkitName.wx])
    def test_reset_without_destroy_wx(self):
        # Characterization test:
        # UI.reset(destroy=False) destroys all editor controls, but leaves
        # editors and ui children intact

        import wx

        foo = FooDialog()
        with create_ui(foo) as ui:

            self.assertEqual(len(ui._editors), 2)
            self.assertIsInstance(
                ui._editors[0], traitsui.wx.text_editor.SimpleEditor
            )
            self.assertIsInstance(
                ui._editors[0].control, wx.TextCtrl
            )

            ui.reset(destroy=False)

            self.assertEqual(len(ui._editors), 2)
            self.assertIsInstance(
                ui._editors[0], traitsui.wx.text_editor.SimpleEditor
            )
            self.assertIsNone(ui._editors[0].control)

            # children are still there: check first text control
            text_ctrl = ui.control.FindWindowByName("text")
            self.assertIsNotNone(text_ctrl)

    @requires_toolkit([ToolkitName.qt])
    def test_reset_without_destroy_qt(self):
        # Characterization test:
        # UI.reset(destroy=False) destroys all editor controls, but leaves
        # editors and ui children intact

        from pyface import qt

        foo = FooDialog()
        with create_ui(foo) as ui:

            self.assertEqual(len(ui._editors), 2)
            self.assertIsInstance(
                ui._editors[0], traitsui.qt4.text_editor.SimpleEditor
            )
            self.assertIsInstance(ui._editors[0].control, qt.QtGui.QLineEdit)

            ui.reset(destroy=False)

            self.assertEqual(len(ui._editors), 2)
            self.assertIsInstance(
                ui._editors[0], traitsui.qt4.text_editor.SimpleEditor
            )
            self.assertIsNone(ui._editors[0].control)

            # children are still there: check first text control
            text_ctrl = ui.control.findChild(qt.QtGui.QLineEdit)
            self.assertIsNotNone(text_ctrl)

    @requires_toolkit([ToolkitName.wx])
    def test_destroy_after_ok_wx(self):
        # Behavior: after pressing 'OK' in a dialog, the method UI.finish is
        # called and the view control and its children are destroyed

        import wx

        foo = FooDialog()
        with create_ui(foo) as ui:

            # keep reference to the control to check that it was destroyed
            control = ui.control

            # decorate control's `Destroy` function to check that it is called
            control.Destroy = count_calls(control.Destroy)

            # press the OK button and close the dialog
            okbutton = ui.control.FindWindowByName("button", ui.control)
            self.assertEqual(okbutton.Label, 'OK')

            click_event = wx.CommandEvent(
                wx.wxEVT_COMMAND_BUTTON_CLICKED, okbutton.GetId()
            )
            okbutton.ProcessEvent(click_event)

            self.assertIsNone(ui.control)
            self.assertEqual(control.Destroy._n_calls, 1)

    @requires_toolkit([ToolkitName.qt])
    def test_destroy_after_ok_qt(self):
        # Behavior: after pressing 'OK' in a dialog, the method UI.finish is
        # called and the view control and its children are destroyed

        from pyface import qt

        foo = FooDialog()
        with create_ui(foo) as ui:

            # keep reference to the control to check that it was deleted
            control = ui.control

            # decorate control's `deleteLater` function to check that it is
            # called
            control.deleteLater = count_calls(control.deleteLater)

            # press the OK button and close the dialog
            okb = control.findChild(qt.QtGui.QPushButton)
            okb.click()

            self.assertIsNone(ui.control)
            self.assertEqual(control.deleteLater._n_calls, 1)

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_no_spring_trait(self):
        obj = DisallowNewTraits()
        with create_ui(obj):
            pass

        self.assertTrue("spring" not in obj.traits())

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_invalid_state(self):
        # Regression test for enthought/traitsui#983
        obj = MaybeInvalidTrait(name="Name long enough to be valid")
        with create_ui(obj) as ui:
            editor, = ui.get_editors("name")
            self.assertFalse(editor.invalid)

            obj.name = "too short"
            self.assertTrue(editor.invalid)


# Regression test on an AttributeError commonly seen (enthought/traitsui#1145)
# Code in ui_panel makes use toolkit specific attributes on the toolkit
# specific Editor
ToolkitSpecificEditor = toolkit_object("editor:Editor")


def get_event_name(event):
    from pyface.qt import QtCore


if is_qt():

    # The following code is typical in Qt editors and looks reasonable.
    # However an attribute error occurs in dispose if we don't hide the
    # control and its children early.

    from pyface.qt import QtGui, QtCore

    class CustomWidget(QtGui.QWidget):

        def __init__(self, editor, parent=None):
            super(CustomWidget, self).__init__()
            self._some_editor = editor

        def sizeHint(self):
            if self._some_editor.factory is None:
                hint = "  <-------- HERE"
            else:
                hint = ""
            parent = self.parent()
            print(f"{self} sizeHint is called. factory is {self._some_editor.factory} {hint}, parent is {parent}")
            assert self._some_editor.factory is not None
            return super().sizeHint()

        def event(self, event):
            result = super().event(event)
            print(self, get_qt_event_name(event), "hidden state: ", self.isHidden(), "visibility: ", self.isVisible())
            return result

    class EditorWithCustomWidget(ToolkitSpecificEditor):

        def init(self, parent):
            # This example reproduces a failure scenario where sizeHint tries
            # to access a factory attribute that has been reset to None.
            # We have two widgets, where one of them is created with a nested
            # UI. When the nested UI is disposed, the original AttributeError
            # is caused by the neighboring widgets trying to resize / repaint /
            # ... adjust to fit the layout. These do not happen if the widgets
            # are made to be hidden first before dispose is called.
            self.control = QtGui.QSplitter(QtCore.Qt.Horizontal)

            widget = CustomWidget(editor=self)
            self.control.addWidget(widget)
            self.control.setStretchFactor(0, 2)

            self._widget2 = CustomWidget(editor=self)
            self.control.addWidget(self._widget2)

            self._ui = self.edit_traits(
                parent=self.control,
                kind="subpanel",
                view=View(Item("_", label="DUMMY"), width=100, height=100),
            )
            print("nested UI control", self._ui.control)
            self.control.addWidget(self._ui.control)

            self._button = QtGui.QPushButton()
            self._button.setText("Close UI")
            self._button.clicked.connect(self.dispose_inner_ui)
            self.control.addWidget(self._button)

            self._button2 = QtGui.QPushButton()
            self._button2.setText("Close custom widget")
            self._button2.clicked.connect(self.dispose_custom_widget)
            self.control.addWidget(self._button2)

        def dispose(self):
            self.dispose_inner_ui()
            super().dispose()

        def dispose_inner_ui(self):
            if self._ui is not None:
                print("Disposing inner UI")
                self._ui.dispose()
                self._ui = None
                self._button.setParent(None)

        def dispose_custom_widget(self):
            if self._widget2 is not None:
                print("Disposing custom widget")
                self._widget2.setParent(None)
                self._widget2.hide()
                self._widget2.deleteLater()
                self._button2.setParent(None)
                self._widget2 = None

        def update_editor(self):
            pass


if is_wx():

    # Mimic causing a cascade of events where a handler to be called
    # will require control/factory/... attributes that will be set
    # to None in dispose. e.g. In enthought/traitsui#1073, the user closes the
    # UI and that action causes a cascade of new events.
    import wx
    from traitsui.wx.helper import TraitsUIPanel

    class EditorWithCustomWidget(ToolkitSpecificEditor):  # noqa: F811

        def init(self, parent):
            self.control = TraitsUIPanel(parent, -1)

            sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.control.text1 = wx.TextCtrl(parent, -1, "dummy")
            sizer.Add(self.control.text1, 0, wx.LEFT | wx.EXPAND, 4)
            self.control.text2 = wx.TextCtrl(parent, -1, "dummy")
            sizer.Add(self.control.text2, 0, wx.LEFT | wx.EXPAND, 4)

            self.control.text1.Bind(
                wx.EVT_KILL_FOCUS, self._update_with_attr_access,
            )
            self.control.text2.Bind(
                wx.EVT_KILL_FOCUS, self._update_with_attr_access,
            )
            self.control.SetSizerAndFit(sizer)
            self._count = 0

        def _update_with_attr_access(self, event):
            if self._count > 1:
                # prevent infinite loop
                return

            # Test objective: We should not run into AttributeError here
            assert self.control is not None

            if event.GetEventObject() is self.control.text1:
                self.control.text2.SetFocus()
                self._count += 1
            if event.GetEventObject() is self.control.text2:
                self.control.text1.SetFocus()
                self._count += 1

        def update_editor(self):
            # Trigger cascade of events at initialization.
            self.control.text1.SetFocus()
            self.control.text2.SetFocus()

        def dispose(self):
            super().dispose()


class DummyObject(HasTraits):

    number = Int()


class TestUIDispose(unittest.TestCase):

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_absence_of_attribute_error_from_dispose(self):
        obj = DummyObject()
        view = View(
            Group(
                Item(
                    "number",
                    editor=BasicEditorFactory(klass=EditorWithCustomWidget),
                ),
            ),
        )
        ui = obj.edit_traits(view=view)
        with ensure_closing(ui):
            from pyface.api import GUI
            gui = GUI()
            gui.invoke_later(toolkit().close_control, ui.control)
            with reraise_exceptions():
                gui.start_event_loop()
            self.assertIsNone(ui.control)

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_dispose_inner_ui(self):
        obj = DummyObject()
        view = View(
            Group(
                Item(
                    "number",
                    editor=BasicEditorFactory(klass=EditorWithCustomWidget),
                ),
            ),
        )
        ui = obj.edit_traits(view=view)
        editor, = ui.get_editors("number")

        from pyface.api import GUI
        gui = GUI()
        with ensure_closing(ui):
            # This represents an event handler that causes a nested UI to be
            # disposed.
            gui.invoke_later(editor.dispose_inner_ui)

            # Allowing GUI to process the disposal requests is crucial.
            # This requirement should be satisfied in production setting
            # where the dispose method is part of an event handler.
            # Not doing so before disposing the main UI would be a programming
            # error in tests settings.
            with reraise_exceptions():
                process_cascade_events()

            gui.invoke_later(toolkit().close_control, ui.control)
            with reraise_exceptions():
                gui.start_event_loop()

            self.assertIsNone(ui.control)

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_dispose_custom_widget(self):
        obj = DummyObject()
        view = View(
            Group(
                Item(
                    "number",
                    editor=BasicEditorFactory(klass=EditorWithCustomWidget),
                ),
            ),
        )
        ui = obj.edit_traits(view=view)
        gui = GUI()
        with ensure_closing(ui):
            editor, = ui.get_editors("number")
            # This represents an event handler that causes a nested UI to be
            # disposed.
            gui.invoke_later(editor.dispose_custom_widget)
            with reraise_exceptions():
                process_cascade_events()

            gui.invoke_later(toolkit().close_control, ui.control)
            with reraise_exceptions():
                gui.start_event_loop()
            self.assertIsNone(ui.control)


import contextlib

@contextlib.contextmanager
def ensure_closing(ui):
    gui = GUI()
    try:
        yield
    finally:
        if ui.control is not None:
            toolkit().destroy_control(ui.control)
        with reraise_exceptions():
            process_cascade_events()


def get_qt_event_name(event):
    event_to_name = {
        event: name for name, event in vars(QtCore.QEvent).items()
        if isinstance(event, int)
    }
    return event_to_name.get(event.type(), "Unknown")
