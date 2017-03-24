#!/usr/bin/python
# -*- coding: utf-8 -*-
from entropyfw import Module
import numbers

from .callbacks import Datalog
import os

"""
module
Created by otger on 23/03/17.
All rights reserved.
"""

class EntropyEventLogger(Module):
    name = 'eventlogger'

    def __init__(self, dealer, name=None, print_data=False):
        Module.__init__(self, name=name, dealer=dealer)
        self.data = LogDataHolder()
        self.print_data = print_data

    def exit(self):
        pass

    def register_event(self, event_name):
        """
        Add event to log its values
        :param event_name:
        :return:
        """
        self.register_callback(Datalog, event_name)

    def add_data(self, event):
        d = self.data.add(event)
        if self.print_data:
            print(d)


class LogDataHolder(object):

    def __init__(self):
        self.sets = {}

    def add(self, event):
        if event.full_id not in self.sets:
            self.sets[event.full_id] = LogDataSet()
        return self.sets[event.full_id].add(event)

    def save_to_file(self, path='/tmp'):
        for k,v in self.sets:
            fname = os.path.join(path, k)
            v.save_file(fname)


class LogDataSet(object):
    def __init__(self):
        self.items = []
        self.values = []

    def add(self, event):
        l = LogData(event)
        self.items = set(list(self.items).extend(l.values.keys()))
        self.values.append(l)
        return l

    def save_to_file(self, file):
        with open(file, 'w') as f:
            f.write(', '.join(str(x) for x in self.items))
            for el in self.values:
                values = [str(el.values.get(x, '')) for x in self.items]
                f.write('{0}, {1}'.format(el.ts, ', '.join(values)))


class LogData(object):
    def __init__(self, event):
        self.ts = event.ts
        if isinstance(event.value, (list, tuple)):
            self.values = {'item_{0}'.format(ix):v for ix, v in enumerate(event.value)}
        elif isinstance(event.value, dict):
            self.values = event.value
        elif isinstance(event.value, numbers.Number):
            self.values = {event.full_id:event.value}

    def __str__(self):
        return '{0}, {1}'.format(self.ts, ', '.join([str(x) for x in self.values.values()]))