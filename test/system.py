#!/usr/bin/python
# -*- coding: utf-8 -*-
from entropyfw import System
from s_tti_cpx.module import EntropyTTiCPX
from entropyfw.common.request import Request
import time
"""
system
Created by otger on 23/03/17.
All rights reserved.
"""


class SystemTC08(System):

    def __init__(self, flask_app):
        System.__init__(self, flask_app)
        self.add_module(EntropyTTiCPX())

    def exit(self):
        self.dealer.exit()

    def activate_timer(self, interval):
        r = Request(command_id=0,
                    source='myself',
                    target='picotc08',
                    command='starttimer',
                    arguments={'interval': interval})
        self.dealer.request(r)
        # r.wait_answer()
        # print(r.return_value)
        return r

    def stop_timer(self):
        r = Request(command_id=0,
                    source='myself',
                    target='picotc08',
                    command='stoptimer',
                    arguments={})
        self.dealer.request(r)
        # r.wait_answer()
        # print(r.return_value)
        return r

    def list_functionality(self):
        r = Request(command_id=0,
                    source='myself',
                    target='picotc08',
                    command='listregisteredactions')
        self.dealer.request(r)
        r.wait_answer()
        s = "Functionality of module 'adder': \n"
        for el in r.return_value:
            s += "\t - {0}\n".format(', '.join([str(x) for x in el]))
        print(s)
        return r

if __name__ == "__main__":
    from entropyfw.logger import log, formatter
    import logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    s = SystemTC08()
    log.info('Created system')
    r = s.activate_timer(2)
    r.wait_answer()
    log.info("Sum('a', 'b') returned: {0}".format(r.return_value))
    s.list_functionality()

    time.sleep(10)
    r = s.stop_timer()
    log.info('Asked stop timer')
    r.wait_answer()

    time.sleep(5)
    s.exit()
