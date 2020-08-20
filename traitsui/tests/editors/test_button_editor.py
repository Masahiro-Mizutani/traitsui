import unittest

from pyface.gui import GUI

from traits.api import Button, HasTraits, List, Str
from traits.testing.api import UnittestTools
from traitsui.api import ButtonEditor, Item, UItem, View
from traitsui.tests._tools import (
    create_ui,
    is_qt,
    is_wx,
    process_cascade_events,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)
from traitsui.testing.tester import command, query
from traitsui.testing.tester.ui_tester import UITester


class ButtonTextEdit(HasTraits):

    play_button = Button("Play")

    play_button_label = Str("I'm a play button")

    values = List()

    traits_view = View(
        Item("play_button", style="simple"),
        Item("play_button", style="custom"),
        Item("play_button", style="readonly"),
        Item("play_button", style="text"),
    )


simple_view = View(
    UItem("play_button", editor=ButtonEditor(label_value="play_button_label")),
    Item("play_button_label"),
    resizable=True,
)


custom_view = View(
    UItem("play_button", editor=ButtonEditor(label_value="play_button_label")),
    Item("play_button_label"),
    resizable=True,
    style="custom",
)


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestButtonEditor(unittest.TestCase, UnittestTools):
    def check_button_text_update(self, view):
        button_text_edit = ButtonTextEdit()

        tester = UITester()
        with tester.create_ui(button_text_edit, dict(view=view)) as ui:
            button = tester.find_by_name(ui, "play_button")
            actual = button.inspect(query.DisplayedText())
            self.assertEqual(actual, "I'm a play button")

            button_text_edit.play_button_label = "New Label"
            actual = button.inspect(query.DisplayedText())
            self.assertEqual(actual, "New Label")

    def test_styles(self):
        # simple smoke test of buttons
        button_text_edit = ButtonTextEdit()
        with UITester().create_ui(button_text_edit):
            pass

    def test_simple_button_editor(self):
        self.check_button_text_update(simple_view)

    def test_custom_button_editor(self):
        self.check_button_text_update(custom_view)

    def check_button_fired_event(self,view):
        button_text_edit = ButtonTextEdit()

        tester = UITester()
        with tester.create_ui(button_text_edit, dict(view=view)) as ui:
            button = tester.find_by_name(ui, "play_button")

            with self.assertTraitChanges(
                    button_text_edit, "play_button", count=1):
                button.perform(command.MouseClick())

    def test_simple_button_editor_clicked(self):
        self.check_button_fired_event(simple_view)

    def test_custom_button_editor_clicked(self):
        self.check_button_fired_event(custom_view)


@requires_toolkit([ToolkitName.qt])
class TestButtonEditorValuesTrait(unittest.TestCase):
    """ The values_trait is only supported by Qt.

    See discussion enthought/traitsui#879
    """

    def get_view(self, style):
        return View(
            Item(
                "play_button",
                editor=ButtonEditor(values_trait="values"),
                style=style,
            ),
        )

    def check_editor_values_trait_init_and_dispose(self, style):
        # Smoke test to check init and dispose when values_trait is used.
        instance = ButtonTextEdit(values=["Item1", "Item2"])
        view = self.get_view(style=style)
        with reraise_exceptions():
            with UITester().create_ui(instance, dict(view=view)):
                pass

            # It is okay to mutate trait after the GUI is disposed.
            instance.values = ["Item3"]

    def test_simple_editor_values_trait_init_and_dispose(self):
        # Smoke test to check init and dispose when values_trait is used.
        self.check_editor_values_trait_init_and_dispose(style="simple")

    def test_custom_editor_values_trait_init_and_dispose(self):
        # Smoke test to check init and dispose when values_trait is used.
        self.check_editor_values_trait_init_and_dispose(style="custom")
