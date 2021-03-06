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

""" This module defines interaction objects that can be passed to
``UIWrapper.inspect`` where the actions represent 'queries'.

Implementations for these actions are expected to return value(s), ideally
without incurring side-effects.
"""


class DisplayedText:
    """ An object representing an interaction to obtain the displayed (echoed)
    plain text.

    E.g. For a textbox using a password styling, the displayed text should
    be a string of platform-dependent password mask characters.

    Implementations should return a ``str``.
    """
    pass
