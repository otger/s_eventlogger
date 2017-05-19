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
    description = "Module that can store events generated and its data"

    def __init__(self, name=None, print_data=False, backup_path=None, backup_interval=300):
        Module.__init__(self, name=name)
        self.backup = Backups(module=self, backup_path=backup_path, backup_interval=backup_interval)
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
        self.backup.save(event)

    def list_event_ids(self):
        """
        Returns a list of all events full ids with data logged
        :return:
        """
        return self.data.list_event_ids()

    def save_file(self, path='/tmp', event_id=None):
        self.data.save_to_file(path, event_id=None)

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
        self._started_on = get_utc_ts()

    def add(self, event):
        if event.full_id not in self.sets:
            self.sets[event.full_id] = LogDataSet(event)
        return self.sets[event.full_id].add(event)

    def save_to_file(self, path='/tmp', event_id=None):
        if event_id is None:
            for k in self.sets.keys():
                self.save_to_file(path=path, event_id=k)
                return
        if event_id not in self.sets:
            raise Exception('event_id do not exist')
        fname = os.path.join(path, '{}.{}'.format(self._started_on, event_id))
        self.sets[event_id].save_to_file(fname)

    def as_csv_str(self, event_id, max_items=0):
        return self.sets[event_id].as_csv_string(max_items)

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
                'total_elements': len(self.values), 'values': []}
        for el in self.values[-max_items:]:
            data['values'].append({'utc_ts': el.ts, 'values': el.as_list(self.fields)})
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


class Backups(object):
    def __init__(self, module, backup_path, backup_interval=60):
        self.module = module
        self.backup_path = backup_path
        self.interval = backup_interval
        self._ts_saved = {}

    def save(self, event):
        if self.backup_path:
            if event.full_id not in self._ts_saved or event.ts - self._ts_saved[event.full_id] > self.interval:
                self.module.save_file(path=self.backup_path, event_id=event.full_id)
                self._ts_saved[event.full_id] = event.ts