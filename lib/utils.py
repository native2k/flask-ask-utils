#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from pprint import pformat
from flask_ask import statement, question, session
from inspect import getargvalues, stack

log = logging.getLogger('utils')

logLevel = logging.INFO


def logArgvalues():
    if log.isEnabledFor(logLevel):
        posname, kwname, args = getargvalues(stack()[1][0])[-3:]
        posargs = args.pop(posname, [])
        args.update(args.pop(kwname, []))

        log.log(logLevel, '===== FUNCTION -> [%s]' % (stack()[1][3], ))
        log.log(logLevel, 'Args: %s - %s' % (pformat(posargs), args))
        log.log(logLevel, 'session: %s' % (session.get('sessionId'), ))
        log.log(logLevel, 'user: %s' % (session.get('user', {}).get('userId'), ))
        log.log(logLevel, 'attributes: %s' % (pformat(session.attributes), ))



def doReprompt(text, reprompt='', joinText=True):
    if reprompt:
        log.log(logLevel, '>>  "%s"  <<' % text)
        if joinText:
            text = " ".join([text, reprompt])
    else:
        reprompt = text
    log.log(logLevel, '>>> "%s" <<<' % reprompt)
    return question(text.encode('utf-8')).reprompt(reprompt.encode('utf-8'))


def doQuestion(text):
    log.log(logLevel, '>> "%s" <<' % text)
    return question(text.encode('utf-8'))


def doSay(text):
    log.log(logLevel, '>>! "%s" !<<' % text)
    # return question(text.encode('utf-8'))
    return statement(text.encode('utf-8'))
