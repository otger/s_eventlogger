#!/usr/bin/python
# -*- coding: utf-8 -*-
from entropyfw import Module
from entropyfw.common import get_utc_ts, utc_ts_string
import numbers

from .callbacks import Datalog
from .exceptions import UnknownFileType
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

    def add_log(self, event_name):
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

    def save_file(self, path='/tmp'):
        self.data.save_to_file(path)


class LogDataHolder(object):

    def __init__(self):
        self.sets = {}

    def add(self, event):
        if event.full_id not in self.sets:
            self.sets[event.full_id] = LogDataSet(event)
        return self.sets[event.full_id].add(event)

    def save_to_file(self, path='/tmp'):
        for k, v in self.sets.items():
            fname = os.path.join(path, k)
            v.save_to_file(fname)


class LogDataSet(object):
    def __init__(self, event):
        self.event_full_id = event.full_id
        self.items = []
        self.values = []
        self.ts_created = get_utc_ts()
        self.ts_last_event = event.ts

    def add(self, event):
        l = LogData(event)
        event_keys = l.values.keys()
        print(event_keys)
        tmp = list(self.items)
        tmp.extend(event_keys)
        self.items = sorted(set(tmp))
        self.values.append(l)
        self.ts_last_event = event.ts
        return l

    def save_csv(self, path):
        with open(path, 'w') as f:
            now = get_utc_ts()
            f.write("# CSV file for events '{0}'\n".format(self.event_full_id))
            f.write("#   - Data set created at: {0} ({1})\n".format(utc_ts_string(self.ts_created), self.ts_created))
            f.write("#   - Last event: {0} ({1})\n".format(utc_ts_string(self.ts_last_event), self.ts_last_event))
            f.write("#   - File generated at: {0} ({1})\n".format(utc_ts_string(now), now))
            f.write("#   - Number of events: {0}\n".format(len(self.values)))
            f.write('timestamp, {0}\n'.format(', '.join(str(x) for x in self.items)))
            for el in self.values:
                f.write(el.as_csv(items=self.items))

    def save_to_file(self, path, ftype='csv'):
        if ftype == 'csv':
            self.save_csv(path)
        else:
            raise UnknownFileType("{0} is an unknown file type".format(ftype))


class LogData(object):
    def __init__(self, event):
        self.ts = event.ts
        if isinstance(event.value, (list, tuple)):
            self.values = {'item_{0}'.format(ix): v for ix, v in enumerate(event.value)}
        elif isinstance(event.value, dict):
            self.values = event.value
        elif isinstance(event.value, numbers.Number):
            self.values = {event.full_id: event.value}
        else:
            self.values = {}

    def __str__(self):
        return '{0}, {1}'.format(self.ts, ', '.join([str(x) for x in self.values.values()]))

    def as_csv(self, separator=', ', items=None):
        if not items:
            items = sorted(self.values.keys())
        values = [str(self.values.get(x, '')) for x in items]
        return '{0}, {1}\n'.format(self.ts, separator.join(values))