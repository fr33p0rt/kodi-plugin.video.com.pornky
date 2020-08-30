# -*- coding: utf-8 -*-

from filter import Filter
from res import Res


class Cfg:
    res = Res.MAX # Res(0)
    filter = Filter.OFF # Filter(1)
    cat = False
    filter_items = None
    search_items = None

    disable_login = False

    username = ''
    password = ''
    cookie_PHPSESSID = ''
    cookie_XSAE = ''
