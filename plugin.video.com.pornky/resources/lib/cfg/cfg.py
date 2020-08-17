# -*- coding: utf-8 -*-

from filter import Filter
from res import Res


class Cfg:
    res = Res.MAX # Res(0)
    filter = Filter.OFF # Filter(1)
    cat = False
    filteritems = None
    searchitems = None
