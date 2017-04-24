#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import render_template, abort, Response
from jinja2 import TemplateNotFound
from entropyfw.common import get_utc_ts
import datetime
from entropyfw.system.web.blueprints import EntropyBlueprint

__author__ = 'otger'


# def get_blueprint(mod_name):
#     tc08bp = EntropyBlueprint('tc08', __name__,
#                               template_folder='templates')
#
#     @tc08bp.route('/')
#     def show():
#         try:
#             return render_template('tc08/index.html', mod_name=mod_name, data=tc08bp.global_data)
#         except TemplateNotFound:
#             abort(404)
#
#     return tc08bp

def get_blueprint(mod_name):

    tc08bp = EventLoggerBluePrint(mod_name, __name__,
                                  template_folder='templates')

    return tc08bp


class EventLoggerBluePrint(EntropyBlueprint):
    def register_routes(self):
        self.add_url_rule('/', 'index', self.index)
        self.add_url_rule('/chart/<event_id>', 'chart', self.chart)
        self.add_url_rule('/csv/<event_id>', 'csv', self.csv)
        self.add_url_rule('/table/<event_id>', 'table', self.table)

    def index(self):
        try:
            data = {'mod_name': self.name,
                    'status': self.mod_parent.data.status}
            return self.render_template('eventlogger/index.html', data=data)
        except TemplateNotFound:
            abort(404)

    def chart(self, event_id):
        try:
            data = {'event_id': event_id}
            return self.render_template('eventlogger/chart.html', data=data)
        except TemplateNotFound:
            abort(404)

    def csv(self, event_id):
        data = self.mod_parent.data.as_csv_str(event_id)
        date = datetime.datetime.utcfromtimestamp(get_utc_ts()).strftime('%Y%m%d%H%M%S')
        return Response(data,
                        mimetype="text/plain",
                        headers={"Content-Disposition":
                                 "attachment;filename={}-{}.csv".format(date, event_id)})

    def table(self, event_id):
        try:
            data = {'event_id': event_id,
                    'event_dataset': self.mod_parent.get_data(event_id)}
            return self.render_template('eventlogger/table.html', data=data)
        except TemplateNotFound:
            abort(404)

