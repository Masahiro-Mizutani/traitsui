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
import wx

from traitsui.wx.enum_editor import (
    ListEditor,
    RadioEditor,
    SimpleEditor,
)
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.base_classes import _BaseSourceWithLocation
from traitsui.testing.tester.wx import helpers


class _IndexedListEditor(_BaseSourceWithLocation):
    """ Wrapper class for EnumListEditor and Index.
    """
    source_class = ListEditor
    locator_class = locator.Index
    handlers = [
        (command.MouseClick, (lambda wrapper, _: helpers.mouse_click_listbox(
            control=wrapper.target.source.control,
            index=wrapper.target.location.index,
            delay=wrapper.delay))),
    ]


class _IndexedRadioEditor(_BaseSourceWithLocation):
    """ Wrapper class for EnumRadioEditor and Index.
    """
    source_class = RadioEditor
    locator_class = locator.Index
    handlers = [
        (command.MouseClick,
            (lambda wrapper, _: helpers.mouse_click_radiobutton_child_in_panel(
                control=wrapper.target.source.control,
                index=wrapper.target.location.index,
                delay=wrapper.delay))),
    ]


class _IndexedSimpleEditor(_BaseSourceWithLocation):
    """ Wrapper class for Simple EnumEditor and Index.
    """
    source_class = SimpleEditor
    locator_class = locator.Index
    handlers = [
        (command.MouseClick,
            (lambda wrapper, _: helpers.mouse_click_combobox_or_choice(
                control=wrapper.target.source.control,
                index=wrapper.target.location.index,
                delay=wrapper.delay))),
    ]


def simple_displayed_text_handler(wrapper, interaction):
    """ Handler function used to query DisplayedText for Simple Enum Editor.
    Note that depending on the factories evaluaute trait, the control for a
    Simple Enum Editor can either be a wx.ComboBox or a wx.Choice.

    Parameters
    ----------
    wrapper : UIWrapper
        The UIWrapper containing that object with text to be displayed.
    interaction : query.DisplayedText
        Unused in this function but included to match the expected format of a
        handler.  Should only be query.DisplayedText
    """
    control = wrapper.target.control
    if isinstance(control, wx.ComboBox):
        return control.GetValue()
    else:  # wx.Choice
        return control.GetString(control.GetSelection())


def radio_displayed_text_handler(wrapper, interaction):
    """ Handler function used to query DisplayedText for EnumRadioEditor.

    Parameters
    ----------
    wrapper : UIWrapper
        The UIWrapper containing that object with text to be displayed.
    interaction : query.DisplayedText
        Unused in this function but included to match the expected format of a
        handler.  Should only be query.DisplayedText
    """
    children_list = wrapper.target.control.GetSizer().GetChildren()
    for index in range(len(children_list)):
        if children_list[index].GetWindow().GetValue():
            return children_list[index].GetWindow().GetLabel()


def register(registry):
    """ Registry location and interaction handlers for EnumEditor.

    Parameters
    ----------
    registry : InteractionRegistry
    """
    _IndexedListEditor.register(registry)
    _IndexedRadioEditor.register(registry)
    _IndexedSimpleEditor.register(registry)

    simple_editor_text_handlers = [
        (command.KeyClick,
            (lambda wrapper, interaction: helpers.key_click_combobox(
                control=wrapper.target.control,
                interaction=interaction,
                delay=wrapper.delay))),
        (command.KeySequence,
            (lambda wrapper, interaction: helpers.key_sequence_text_ctrl(
                control=wrapper.target.control,
                interaction=interaction,
                delay=wrapper.delay))),
        (query.DisplayedText, simple_displayed_text_handler)
    ]

    for interaction_class, handler in simple_editor_text_handlers:
        registry.register_handler(
            target_class=SimpleEditor,
            interaction_class=interaction_class,
            handler=handler
        )

    registry.register_handler(
        target_class=RadioEditor,
        interaction_class=query.DisplayedText,
        handler=radio_displayed_text_handler,
    )
    registry.register_handler(
        target_class=ListEditor,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.target.control.GetString(
            wrapper.target.control.GetSelection()),
    )
