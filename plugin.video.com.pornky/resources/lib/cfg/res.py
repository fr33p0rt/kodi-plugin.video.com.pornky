# -*- coding: utf-8 -*-

from enum34 import Enum

class Res(Enum):
    MAX = 0
    M1080 = 1
    M720 = 2
    M480 = 3
    M320 = 4
    MIN = 5

    def res(self):
        return (999999, 1080, 720, 480, 360, 0)[self.value]
