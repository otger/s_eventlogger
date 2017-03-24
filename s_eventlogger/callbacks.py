#!/usr/bin/python
# -*- coding: utf-8 -*-
from entropyfw import Callback

"""
callbacks
Created by otger on 23/03/17.
All rights reserved.
"""


class Datalog(Callback):
    name = 'datalog'
    description = "Logs events data"
    version = "0.1"

    def __init__(self, event, manager, module):
        Callback.__init__(self, event, manager, module)

    def functionality(self):
        self.module.add_data(self.event)
