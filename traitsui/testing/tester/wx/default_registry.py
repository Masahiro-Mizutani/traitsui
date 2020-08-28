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

from traitsui.testing.tester.registry import TargetRegistry
from traitsui.testing.tester.wx import located_object_handlers
from traitsui.testing.tester.wx.implementation import (
    button_editor,
    list_editor,
    range_editor,
    text_editor,
)


def get_default_registry():
    """ Creates a default registry for UITester that is wx specific.

    Returns
    -------
    registry : TargetRegistry
        The default registry containing implementations for TraitsUI editors
        that is wx specific.
    """
    registry = TargetRegistry()

    located_object_handlers.LocatedTextbox.register(registry)

    # ButtonEditor
    button_editor.register(registry)

    # TextEditor
    text_editor.register(registry)

    # RangeEditor
    range_editor.register(registry)

    list_editor.register(registry)

    return registry
