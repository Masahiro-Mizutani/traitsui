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

""" This module provides functions for registering interaction handlers
and location solvers for common Qt GUI components.
"""

from traitsui.testing.tester import command, query
from traitsui.testing.tester.qt4 import helpers


def register_editable_textbox_handlers(registry, target_class, widget_getter):
    """ Register common interactions for an editable textbox (in Qt)

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    target_class : subclass of type
        The type of target being wrapped in a UIWrapper on which the
        interaction will be performed.
    widget_getter : callable(wrapper: UIWrapper) -> QWidget
        A callable to return a Qt widget for editing text, i.e. QLineEdit
        or QTextEdit.
    """
    handlers = [
        (command.KeySequence,
            (lambda wrapper, interaction: helpers.key_sequence_textbox(
                widget_getter(wrapper), interaction, wrapper.delay))),
        (command.KeyClick,
            (lambda wrapper, interaction: helpers.key_click_qwidget(
                widget_getter(wrapper), interaction, wrapper.delay))),
        (command.MouseClick,
            (lambda wrapper, _: helpers.mouse_click_qwidget(
                widget_getter(wrapper), wrapper.delay))),
        (query.DisplayedText,
            lambda wrapper, _: helpers.displayed_text_qobject(
                widget_getter(wrapper))),
    ]
    for interaction_class, handler in handlers:
        registry.register_handler(
            target_class=target_class,
            interaction_class=interaction_class,
            handler=handler,
        )
