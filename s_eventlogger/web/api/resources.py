#!/usr/bin/python
# -*- coding: utf-8 -*-
from entropyfw.api.rest import ModuleResource, REST_STATUS
from flask import jsonify, make_response
from flask_restful import reqparse
from entropyfw.common import get_utc_ts
from PicoController.common.definitions import THERMOCOUPLES, UNITS
from .logger import log

"""
resources
Created by otger on 29/03/17.
All rights reserved.
"""


class RegisterEvent(ModuleResource):
    url = 'register_event'
    description = "Register events to be logged. All events that match provided regular expression will be logged"

    def __init__(self, module):
        super(RegisterEvent, self).__init__(module)
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('event_re', type=str, required=True, location='json')

    def post(self):
        args = self.reqparse.parse_args()
        try:
            self.module.add_log(args['event_re'])
        except Exception as ex:
            log.exception('Exception when starting status publication loop')
            return self.jsonify_return(status=REST_STATUS.Error, result=str(ex), args=args)
        else:
            return self.jsonify_return(status=REST_STATUS.Done, result=None, args=args)


class GetData(ModuleResource):
    url = 'get_data'
    description = "Dumps data of an specific event"

    def __init__(self, module):
        super(GetData, self).__init__(module)
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('event_id', type=str, required=True, location='json')
        self.reqparse.add_argument('max_items', type=int, location='json')

    def post(self):
        args = self.reqparse.parse_args()
        max_items = args.get('max_items', 0)
        try:
            values = self.module.as_dict(args['event_id'], max_items)
        except Exception as ex:
            log.exception('Exception when starting status publication loop')
            return self.jsonify_return(status=REST_STATUS.Error, result=str(ex), args=args)
        else:
            return self.jsonify_return(status=REST_STATUS.Done, result=values, args=args)


class ListEvents(ModuleResource):
    url = 'list_events'
    description = "List events for which it has data"

    def __init__(self, module):
        super(ListEvents, self).__init__(module)

    def post(self):

        try:
            values = self.module.list_events_ids()
        except Exception as ex:
            log.exception('Exception when starting status publication loop')
            return self.jsonify_return(status=REST_STATUS.Error, result=str(ex))
        else:
            return self.jsonify_return(status=REST_STATUS.Done, result=values)


class DownloadCSV(ModuleResource):
    url = 'get_csv'
    description = "Dumps data of an specific event"
    # check: http://stackoverflow.com/questions/20243850/flask-restful-return-custom-response-format
    # check: http://code.runnable.com/UiIdhKohv5JQAAB6/how-to-download-a-file-generated-on-the-fly-in-flask-for-python

    def __init__(self, module):
        super(DownloadCSV, self).__init__(module)
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('event_id', type=str, required=True, location='json')
        self.reqparse.add_argument('max_items', type=int, location='json')

    def post(self):
        args = self.reqparse.parse_args()
        max_items = args.get('max_items', 0)
        response = make_response(self.module.as_csv_str(args['event_id'], max_items))
        response.headers["Content-Disposition"] = "attachment; filename=books.csv"

        return response


def get_api_resources():
    return [RegisterEvent, GetData, DownloadCSV, ListEvents]
