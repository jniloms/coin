# This program was made by:
#
# Nilo Martins and Ricardo Paranhos
#
# to a class of Computer Intelligence
#
# by Prof. Fernando Buarque, PhD
#
# from University of Pernambuco – UPE,
# School of Engineering – POLI
#
# Year 2018
#
# This software are licensed by GPLv3
#
# Contact: jniloms@gmail.com



# This class define a Fuzzy set in shape of trapeze

class TrapezeFuzzyGroup(object):

    def __str__(self):
        return self.name

    def __init__(self, baseleft, topleft, topright, baseright, value, name='unknown'):
        self.baseleft = baseleft
        self.topleft = topleft
        self.topright = topright
        self.baseright = baseright
        self.value = value
        self.name = name

    def fit(self, x):
        if x < self.baseleft:
            return 0.0
        else:
            if x < self.topleft:
                size = self.topleft - self.baseleft
                return (x - self.baseleft) * self.value / size
            elif x < self.topright:
                return self.value
            elif x < self.baseright:
                size = self.baseright - self.topright
                return (self.value - ((x - self.topright) * self.value / size))
            else:
                return 0.0

# Implementation of Fuzzyfy and Defuzzyfy methods

class Fuzzy(object):

    def __init__(self, fuzzygroups=[]):
        fuzzygroups.sort(key=lambda x: x.value)
        self.fuzzygroups = fuzzygroups

    def fuzzyfy(self, value):
        r = 0
        for i in self.fuzzygroups:
            r += i.fit(value)
        return r

    def defuzzyfy(self, x):
        i = len(self.fuzzygroups) - 1
        while i > 0:
            if x > ((self.fuzzygroups[i].value + self.fuzzygroups[i - 1].value) / 2):
                return self.fuzzygroups[i]
            i -= 1
        if x > (self.fuzzygroups[0].value / 2):
            return self.fuzzygroups[0]
        else:
            return None