#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from flask_ask import statement, question, session
from inspect import getargvalues, stack

log = logging.getLogger('utils')


def logArgvalues():
    if log.isEnabledFor(logging.DEBUG):
        posname, kwname, args = getargvalues(stack()[1][0])[-3:]
        posargs = args.pop(posname, [])
        args.update(args.pop(kwname, []))

        log.debug('===== FUNCTION -> [%s]' % (stack()[1][3], ))
        log.debug('Args: %s - %s' % (posargs, args))
        log.debug('session: %s' % (session.get('sessionId'), ))
        log.debug('user: %s' % (session.get('user', {}).get('userId'), ))


def doReprompt(text, reprompt='', joinText=True):
    if reprompt:
        log.debug('>>  "%s"  <<' % text)
        if joinText:
            text = " ".join([text, reprompt])
    else:
        reprompt = text
    log.debug('>>> "%s" <<<' % reprompt)
    return question(text.encode('utf-8')).reprompt(reprompt.encode('utf-8'))


def doQuestion(text):
    log.debug('>> "%s" <<' % text)
    return question(text.encode('utf-8'))


def doSay(text):
    log.debug('>>! "%s" !<<' % text)
    # return question(text.encode('utf-8'))
    return statement(text.encode('utf-8'))
