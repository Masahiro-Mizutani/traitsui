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

import importlib

from traits.etsconfig.api import ETSConfig

from traitsui.testing.tester.registry import TargetRegistry


def get_default_registry():
    # side-effect to determine current toolkit
    module = importlib.import_module(".default_registry", "traitsui.testing.tester." + ETSConfig.toolkit)
    return module.get_default_registry()