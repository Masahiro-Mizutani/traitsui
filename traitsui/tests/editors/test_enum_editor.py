import contextlib
import platform
import unittest

from traits.api import Enum, HasTraits, Int, List
from traitsui.api import EnumEditor, UItem, View
from traitsui.tests._tools import (
    create_ui,
    get_all_button_status,
    is_qt,
    is_wx,
    process_cascade_events,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


is_windows = platform.system() == "Windows"


class EnumModel(HasTraits):

    value = Enum("one", "two", "three", "four")


def get_view(style):
    return View(UItem("value", style=style), resizable=True)


def get_evaluate_view(style, auto_set=True, mode="radio"):
    return View(
        UItem(
            "value",
            editor=EnumEditor(
                evaluate=True,
                values=["one", "two", "three", "four"],
                auto_set=auto_set,
                mode=mode,
            ),
            style=style,
        ),
        resizable=True,
    )


def get_combobox_text(combobox):
    """ Return the text given a combobox control """
    if is_wx():
        import wx

        if isinstance(combobox, wx.Choice):
            return combobox.GetString(combobox.GetSelection())
        else:
            return combobox.GetValue()

    elif is_qt():
        return combobox.currentText()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def set_combobox_text(combobox, text):
    """ Set the text given a combobox control """
    if is_wx():
        import wx

        if isinstance(combobox, wx.Choice):
            event_type = wx.EVT_CHOICE.typeId
            event = wx.CommandEvent(event_type, combobox.GetId())
            event.SetString(text)
            wx.PostEvent(combobox, event)
        else:
            combobox.SetValue(text)
            event_type = wx.EVT_COMBOBOX.typeId
            event = wx.CommandEvent(event_type, combobox.GetId())
            event.SetString(text)
            wx.PostEvent(combobox, event)

    elif is_qt():
        combobox.setEditText(text)

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def set_combobox_index(combobox, idx):
    """ Set the choice index given a combobox control and index number """
    if is_wx():
        import wx

        if isinstance(combobox, wx.Choice):
            event_type = wx.EVT_CHOICE.typeId
        else:
            event_type = wx.EVT_COMBOBOX.typeId
        event = wx.CommandEvent(event_type, combobox.GetId())
        text = combobox.GetString(idx)
        event.SetString(text)
        event.SetInt(idx)
        wx.PostEvent(combobox, event)

    elif is_qt():
        combobox.setCurrentIndex(idx)

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def finish_combobox_text_entry(combobox):
    """ Finish text entry given combobox. """
    if is_wx():
        import wx

        event = wx.CommandEvent(wx.EVT_TEXT_ENTER.typeId, combobox.GetId())
        wx.PostEvent(combobox, event)

    elif is_qt():
        combobox.lineEdit().editingFinished.emit()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def click_radio_button(widget, button_idx):
    """ Simulate a radio button click given widget and button number. Assumes
    all sizer children (wx) or layout items (qt) are buttons."""
    if is_wx():
        import wx

        sizer_items = widget.GetSizer().GetChildren()
        button = sizer_items[button_idx].GetWindow()
        event = wx.CommandEvent(wx.EVT_RADIOBUTTON.typeId, button.GetId())
        event.SetEventObject(button)
        wx.PostEvent(widget, event)

    elif is_qt():
        widget.layout().itemAt(button_idx).widget().click()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def get_list_widget_text(list_widget):
    """ Return the text of currently selected item in given list widget. """
    if is_wx():
        selected_item_idx = list_widget.GetSelection()
        return list_widget.GetString(selected_item_idx)

    elif is_qt():
        return list_widget.currentItem().text()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def set_list_widget_selected_index(list_widget, idx):
    """ Set the choice index given a list widget control and index number. """
    if is_wx():
        import wx

        list_widget.SetSelection(idx)
        event = wx.CommandEvent(wx.EVT_LISTBOX.typeId, list_widget.GetId())
        wx.PostEvent(list_widget, event)

    elif is_qt():
        list_widget.setCurrentRow(idx)

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestEnumEditorMapping(unittest.TestCase):

    @contextlib.contextmanager
    def setup_ui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            yield ui.get_editors("value")[0]

    def check_enum_mappings_value_change(self, style, mode):
        class IntEnumModel(HasTraits):
            value = Int()

        enum_editor_factory = EnumEditor(
            values=[0, 1],
            format_func=lambda v: str(bool(v)).upper(),
            mode=mode
        )
        formatted_view = View(
            UItem(
                "value",
                editor=enum_editor_factory,
                style=style,
            )
        )

        with reraise_exceptions(), \
                self.setup_ui(IntEnumModel(), formatted_view) as editor:

            self.assertEqual(editor.names, ["FALSE", "TRUE"])
            self.assertEqual(editor.mapping, {"FALSE": 0, "TRUE": 1})
            self.assertEqual(
                editor.inverse_mapping, {0: "FALSE", 1: "TRUE"}
            )

            enum_editor_factory.values = [1, 0]

            self.assertEqual(editor.names, ["TRUE", "FALSE"])
            self.assertEqual(editor.mapping, {"TRUE": 1, "FALSE": 0})
            self.assertEqual(
                editor.inverse_mapping, {1: "TRUE", 0: "FALSE"}
            )

    def check_enum_mappings_name_change(self, style, mode):
        class IntEnumModel(HasTraits):
            value = Int()
            possible_values = List([0, 1])

        formatted_view = View(
            UItem(
                'value',
                editor=EnumEditor(
                    name="object.possible_values",
                    format_func=lambda v: str(bool(v)).upper(),
                    mode=mode
                ),
                style=style,
            )
        )
        model = IntEnumModel()

        with reraise_exceptions(), \
                self.setup_ui(model, formatted_view) as editor:

            self.assertEqual(editor.names, ["FALSE", "TRUE"])
            self.assertEqual(editor.mapping, {"FALSE": 0, "TRUE": 1})
            self.assertEqual(
                editor.inverse_mapping, {0: "FALSE", 1: "TRUE"}
            )

            model.possible_values = [1, 0]

            self.assertEqual(editor.names, ["TRUE", "FALSE"])
            self.assertEqual(editor.mapping, {"TRUE": 1, "FALSE": 0})
            self.assertEqual(
                editor.inverse_mapping, {1: "TRUE", 0: "FALSE"}
            )

    def test_simple_editor_mapping_values(self):
        self.check_enum_mappings_value_change("simple", "radio")

    def test_simple_editor_mapping_name(self):
        self.check_enum_mappings_name_change("simple", "radio")

    def test_radio_editor_mapping_values(self):
        # FIXME issue enthought/traitsui#842
        if is_wx():
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_enum_mappings_value_change("custom", "radio")
        else:
            self.check_enum_mappings_value_change("custom", "radio")

    def test_radio_editor_mapping_name(self):
        # FIXME issue enthought/traitsui#842
        if is_wx():
            import wx

            with self.assertRaises(wx._core.wxAssertionError):
                self.check_enum_mappings_name_change("custom", "radio")
        else:
            self.check_enum_mappings_name_change("custom", "radio")

    def test_list_editor_mapping_values(self):
        self.check_enum_mappings_value_change("custom", "list")

    def test_list_editor_mapping_name(self):
        self.check_enum_mappings_name_change("custom", "list")


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestSimpleEnumEditor(unittest.TestCase):

    @contextlib.contextmanager
    def setup_gui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            process_cascade_events()
            editor = ui.get_editors("value")[0]
            yield editor

    def check_enum_text_update(self, view):
        enum_edit = EnumModel()

        with reraise_exceptions(), \
                self.setup_gui(enum_edit, view) as editor:

            self.assertEqual(get_combobox_text(editor.control), "one")

            enum_edit.value = "two"
            process_cascade_events()

            self.assertEqual(get_combobox_text(editor.control), "two")

    def check_enum_object_update(self, view):
        enum_edit = EnumModel()

        with reraise_exceptions(), \
                self.setup_gui(enum_edit, view) as editor:

            self.assertEqual(enum_edit.value, "one")

            set_combobox_text(editor.control, "two")
            process_cascade_events()

            self.assertEqual(enum_edit.value, "two")

    def check_enum_index_update(self, view):
        enum_edit = EnumModel()

        with reraise_exceptions(), \
                self.setup_gui(enum_edit, view) as editor:

            self.assertEqual(enum_edit.value, "one")

            set_combobox_index(editor.control, 1)
            process_cascade_events()

            self.assertEqual(enum_edit.value, "two")

    def check_enum_text_bad_update(self, view):
        enum_edit = EnumModel()

        with reraise_exceptions(), \
                self.setup_gui(enum_edit, view) as editor:

            self.assertEqual(enum_edit.value, "one")

            set_combobox_text(editor.control, "t")
            process_cascade_events()

            self.assertEqual(enum_edit.value, "one")

    def test_simple_enum_editor_text(self):
        self.check_enum_text_update(get_view("simple"))

    def test_simple_enum_editor_index(self):
        self.check_enum_index_update(get_view("simple"))

    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_editor_text(self):
        self.check_enum_text_update(get_evaluate_view("simple"))

    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_editor_index(self):
        self.check_enum_index_update(get_evaluate_view("simple"))

    def test_simple_evaluate_editor_bad_text(self):
        self.check_enum_text_bad_update(get_evaluate_view("simple"))

    @unittest.skipIf(is_windows, "Test needs fixing on windows")
    def test_simple_evaluate_editor_object(self):
        self.check_enum_object_update(get_evaluate_view("simple"))

    def test_simple_evaluate_editor_object_no_auto_set(self):
        view = get_evaluate_view("simple", auto_set=False)
        enum_edit = EnumModel()

        with reraise_exceptions(), \
                self.setup_gui(enum_edit, view) as editor:

            self.assertEqual(enum_edit.value, "one")

            set_combobox_text(editor.control, "two")
            process_cascade_events()

            # wx modifies the value without the need to finish entry
            if is_qt():
                self.assertEqual(enum_edit.value, "one")

                finish_combobox_text_entry(editor.control)
                process_cascade_events()

            self.assertEqual(enum_edit.value, "two")

    def test_simple_editor_resizable(self):
        # Smoke test for `qt4.enum_editor.SimpleEditor.set_size_policy`
        enum_edit = EnumModel()
        resizable_view = View(UItem("value", style="simple", resizable=True))

        with reraise_exceptions(), \
                create_ui(enum_edit, dict(view=resizable_view)):
            pass

    def test_simple_editor_rebuild_editor_evaluate(self):
        # Smoke test for `wx.enum_editor.SimpleEditor.rebuild_editor`
        enum_editor_factory = EnumEditor(
            evaluate=True,
            values=["one", "two", "three", "four"],
        )
        view = View(UItem("value", editor=enum_editor_factory, style="simple"))

        with reraise_exceptions(), \
                create_ui(EnumModel(), dict(view=view)):

            enum_editor_factory.values = ["one", "two", "three"]


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestRadioEnumEditor(unittest.TestCase):

    @contextlib.contextmanager
    def setup_gui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            process_cascade_events()
            editor = ui.get_editors("value")[0]
            yield editor

    def test_radio_enum_editor_button_update(self):
        enum_edit = EnumModel()

        with reraise_exceptions(), \
                self.setup_gui(enum_edit, get_view("custom")) as editor:

            # The layout is: one, three, four \n two
            self.assertEqual(
                get_all_button_status(editor.control),
                [True, False, False, False]
            )

            enum_edit.value = "two"
            process_cascade_events()

            self.assertEqual(
                get_all_button_status(editor.control),
                [False, False, False, True]
            )

    def test_radio_enum_editor_pick(self):
        enum_edit = EnumModel()

        with reraise_exceptions(), \
                self.setup_gui(enum_edit, get_view("custom")) as editor:

            self.assertEqual(enum_edit.value, "one")

            # The layout is: one, three, four \n two
            click_radio_button(editor.control, 3)
            process_cascade_events()

            self.assertEqual(enum_edit.value, "two")


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestListEnumEditor(unittest.TestCase):

    @contextlib.contextmanager
    def setup_gui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            process_cascade_events()
            editor = ui.get_editors("value")[0]
            yield editor

    def check_enum_text_update(self, view):
        enum_edit = EnumModel()

        with reraise_exceptions(), \
                self.setup_gui(enum_edit, view) as editor:

            self.assertEqual(get_list_widget_text(editor.control), "one")

            enum_edit.value = "two"
            process_cascade_events()

            self.assertEqual(get_list_widget_text(editor.control), "two")

    def check_enum_index_update(self, view):
        enum_edit = EnumModel()

        with reraise_exceptions(), \
                self.setup_gui(enum_edit, view) as editor:

            self.assertEqual(enum_edit.value, "one")

            set_list_widget_selected_index(editor.control, 1)
            process_cascade_events()

            self.assertEqual(enum_edit.value, "two")

    def test_list_enum_editor_text(self):
        view = View(
            UItem(
                "value",
                editor=EnumEditor(
                    values=["one", "two", "three", "four"],
                    mode="list",
                ),
                style="custom",
            ),
            resizable=True,
        )
        self.check_enum_text_update(view)

    def test_list_enum_editor_index(self):
        view = View(
            UItem(
                "value",
                editor=EnumEditor(
                    values=["one", "two", "three", "four"],
                    mode="list",
                ),
                style="custom",
            ),
            resizable=True,
        )
        self.check_enum_index_update(view)

    def test_list_evaluate_editor_text(self):
        self.check_enum_text_update(get_evaluate_view("custom", mode="list"))

    def test_list_evaluate_editor_index(self):
        self.check_enum_index_update(get_evaluate_view("custom", mode="list"))
