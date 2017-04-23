#!/usr/bin/python
# -*- coding: utf-8 -*-
from entropyfw import Module
from entropyfw.common import get_utc_ts, utc_ts_string
import numbers
from .web.api.resources import get_api_resources
from .web.blueprints import get_blueprint
from .callbacks import Datalog
from .exceptions import UnknownFileType
import os
import io

"""
module
Created by otger on 23/03/17.
All rights reserved.
"""


class EntropyEventLogger(Module):
    name = 'eventlogger'

    def __init__(self, name=None, print_data=False):
        Module.__init__(self, name=name)
        self.data = LogDataHolder()
        self.print_data = print_data
        self.register_blueprint(get_blueprint(self.name))
        for r in get_api_resources():
            self.register_api_resource(r)

    def exit(self):
        pass

    def add_log(self, event_re):
        """
        Add event to log its values
        :param event_re: Regular expression. All events that match this RE will be logged
        :return:
        """
        self.register_callback(Datalog, event_re)

    def add_data(self, event):
        d = self.data.add(event)
        if self.print_data:
            print(d)

    def list_event_ids(self):
        """
        Returns a list of all events full ids with data logged
        :return:
        """
        return self.data.list_event_ids()

    def save_file(self, path='/tmp'):
        self.data.save_to_file(path)

    def get_data(self, event_id, max_items=0):
        """
        Return
        :param event_id: full_id of the event
        :param max_values: Maximum number of data values to return, 0 for all
        :return: dictionary with data and metadata
        """
        return self.data.as_dict(event_id, max_items)

    def as_csv_str(self, event_id, max_items=0):
        return self.data.as_csv_str(event_id, max_items)


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

    def as_csv_str(self, event_id, max_items=0):
        if event_id not in self.sets:
            raise Exception('event_id do not exist')
        return self.sets[event_id].as_csv_str(max_items)

    def list_event_ids(self):
        return self.sets.keys()

    def as_dict(self, event_id, max_items=0):
        if event_id not in self.sets:
            raise Exception('event_id do not exist')
        return self.sets[event_id].as_dict(max_items)

    def _get_status(self):

        return {k: v.status for k, v in self.sets.items()}

    status = property(_get_status)


class LogDataSet(object):
    def __init__(self, event):
        self.event_full_id = event.full_id
        self.fields = []
        self.values = []
        self.ts_created = get_utc_ts()
        self.ts_last_event = event.ts

    def _get_status(self):
        return {'full_id': self.event_full_id,
                'fields': self.fields,
                'values': len(self.values),
                'created': self.ts_created,
                'updated': self.ts_last_event}

    status = property(_get_status)

    def add(self, event):
        l = LogData(event)
        event_keys = l.fields
        tmp = list(self.fields)
        tmp.extend(event_keys)
        self.fields = sorted(set(tmp))
        self.values.append(l)
        self.ts_last_event = event.ts
        return l

    def as_csv_string(self, max_items=0):
        return self.get_as_csv(max_items=max_items).getvalue()

    def get_as_csv(self, f=None, max_items=0):
        """
        writes stored data set into a file object (or StringIO)
        :param f: file interface object
        :param max_elements: Maximum number of elements (0: all)
        :return:
        """
        if f is None:
            f = io.StringIO()
        now = get_utc_ts()
        f.write("# CSV file for events '{0}'\n".format(self.event_full_id))
        f.write("#   - Data set created at: {0} ({1})\n".format(utc_ts_string(self.ts_created), self.ts_created))
        f.write("#   - Last event: {0} ({1})\n".format(utc_ts_string(self.ts_last_event), self.ts_last_event))
        f.write("#   - File generated at: {0} ({1})\n".format(utc_ts_string(now), now))
        f.write("#   - Number of events: {0}\n".format(len(self.values)))
        f.write('timestamp, {0}\n'.format(', '.join(str(x) for x in self.fields)))
        if max_items > 0:
            for el in self.values[-max_items:]:
                f.write(el.as_csv(items=self.fields))
        else:
            for el in self.values:
                f.write(el.as_csv(items=self.fields))
        return f

    def save_csv(self, path, max_items=0):
        with open(path, 'w') as f:
            self.get_as_csv(f, max_items)

    def save_to_file(self, path, ftype='csv'):
        if ftype == 'csv':
            self.save_csv(path)
        else:
            raise UnknownFileType("{0} is an unknown file type".format(ftype))

    def as_dict(self, max_items=0):
        data = {'fields': self.fields, 'created_utc_ts': self.ts_created, 'updated_utc_ts': self.ts_last_event,
                'total_elements': len(self.values), 'values':[]}
        for el in self.values[-max_items:]:
            data['values'].append({'utc_ts': el.ts, 'values':el.as_list(self.fields)})
        data['written_elements'] = len(data['values'])
        return data


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

    def as_list(self, items=None):
        if not items:
            items = sorted(self.values.keys())
        values = [self.values.get(x, '') for x in items]
        return values

    def _get_fields(self):
        return self.values.keys()
    fields = property(_get_fields)