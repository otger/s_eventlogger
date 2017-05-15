#!/usr/bin/python
# -*- coding: utf-8 -*-
from entropyfw import System
from s_pico_tc08.module import EntropyPicoTc08
from s_eventlogger.module import EntropyEventLogger

"""
system
Created by otger on 23/03/17.
All rights reserved.
"""


class SystemLoggerTest(System):

    def __init__(self, flask_app):
        System.__init__(self, flask_app)
        self.add_module(EntropyPicoTc08(name='thermocouples'))
        self.add_module(EntropyEventLogger(name='logger'))

    def exit(self):
        pass


if __name__ == "__main__":
    from entropyfw.logger import log, formatter
    import logging
    from gevent.wsgi import WSGIServer
    from flask import Flask, url_for

    app = Flask(__name__)
    server = WSGIServer(("", 5000), app)
    server.start()

    @app.errorhandler(Exception)
    def all_exception_handler(error):
        log.exception('Whatever exception')

    @app.errorhandler(404)
    def handle_bad_request(e):
        log.exception('Whatever exception')

    def list_routes():
        import urllib
        output = []
        for rule in app.url_map.iter_rules():

            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            methods = ','.join(rule.methods)
            url = url_for(rule.endpoint, **options)
            line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
            output.append(line)

        for line in sorted(output):
            print(line)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    s = SystemLoggerTest(flask_app=app)
    print(app.url_map)

    try:
        server.serve_forever()
    finally:
        s.exit()
