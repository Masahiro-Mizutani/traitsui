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
from traitsui.wx.range_editor import (
    LargeRangeSliderEditor,
    LogRangeSliderEditor,
    RangeTextEditor,
    SimpleSliderEditor,
    SimpleSpinEditor,
)

from traitsui.testing.tester import locator
from traitsui.testing.tester.wx.located_object_handlers import LocatedTextbox

class RangeEditorTextbox(LocatedTextbox):
    pass

def resolve_location_simple_slider(wrapper, location):
    if location == locator.WidgetType.textbox:
        print(wrapper.target)
        return RangeEditorTextbox(textbox=wrapper.target.control.text)

    raise NotImplementedError()


def register(registry):

    targets = [SimpleSliderEditor,
               LogRangeSliderEditor,
               LargeRangeSliderEditor,
               RangeTextEditor]
    for target_class in targets:
        registry.register_solver(
            target_class=target_class,
            locator_class=locator.WidgetType,
            solver=resolve_location_simple_slider,
        )
    RangeEditorTextbox.register(registry)