# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import sys

if sys.hexversion < 0x03000000:
    import _api_level_1_py26_and_below as test
else:
    import _api_level_1 as test

test.run()

