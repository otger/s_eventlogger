#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import render_template, abort
from jinja2 import TemplateNotFound

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

    def index(self):
        try:
            data = {'page_title': self.name,
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
