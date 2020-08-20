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


from pyface.qt import QtCore
from pyface.qt.QtTest import QTest

def mouse_click_qwidget(wrapper, action):
    QTest.mouseClick(
        wrapper.target,
        QtCore.Qt.LeftButton,
        delay=wrapper.delay,
    )