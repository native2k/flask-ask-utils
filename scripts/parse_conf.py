#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import os
import re
import yaml
import types
# from pprint import pformat

parser = argparse.ArgumentParser(description='Convert YAML to Alexa conf files')
parser.add_argument('filename', help='path to input YAML file')

PAT_SLOT = re.compile(r'({\-\|[\w]+})')
PAT_PERMUT = re.compile(r'({[\w\|\.\,\s]+\-?})', re.UNICODE)


def parse_yaml(filename):
    with open(filename) as f:
        data = yaml.safe_load(f.read())

    path = os.path.dirname(filename)
    intents = data.get('intents', {})
    write_intents(
        intents, os.path.join(path, 'intent_schema.json'))
    write_slots(data.get('slots', {}), os.path.join(path, 'slots'))
    write_utterances(
        data.get('utterances', {}), data.get('extutterances', {}),
        [isinstance(i, types.DictType) and i.keys()[0] or i for i in intents],
        os.path.join(path, 'utterances.txt'))


def format_intents(intents):
    for intent in intents:
        if not isinstance(intent, dict):
            yield {
                'intent': intent
            }
            continue
        for intent_name in intent:
            slots = intent[intent_name]
            yield {
                'intent': intent_name,
                'slots': [{
                    'name': slot_name,
                    'type': slot_type
                } for slot_name, slot_type in sorted(slots.items())]
            }


def write_intents(intents, filename):
    with open(filename, 'w') as f:
        f.write(json.dumps({
            'intents': list(format_intents(intents))
        }, indent=2, sort_keys=True, separators=(',', ': ')))


def write_slots(slots, dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    for name, values in slots.items():
        with open(os.path.join(dirname, name), 'w') as f:
            f.write('\n'.join(values))


def format_multipleutterances(line):
    # find all permutations
    permut = [
        k[1:-1].split('|')
        for k in PAT_PERMUT.findall(line)
    ]
    # and replace with format string
    lformat = PAT_PERMUT.sub('{}', line)

    # need to add addition {} because we need them for the final replacement
    for k in PAT_SLOT.findall(line):
        lformat = lformat.replace(k, '{{{{{}}}}}'.format(k[3:-1]))

    if permut:
        replace = [['' if k == '-' else k] for k in permut.pop(0)]

        def addFunc(permut, replace):
            if permut:
                newentrys = permut.pop(0)
                res = []
                for k in replace:
                    for e in newentrys:
                        newEle = k[:]
                        newEle.append('' if e == '-' else e)
                        res.append(newEle)
                return addFunc(permut, res)
            else:
                return replace

        # create all possible combinations
        return [
            lformat.format(*p)
            for p in addFunc(permut, replace)
        ]
    else:
        return [lformat.format()]


def format_utterances(utterances, extutterances, intents):
    return '\n'.join(sorted(set([
            u'{} {}'.format(intent, single)
            for intent, lines in sorted(extutterances.items()) if intent in intents
            for line in lines
            for single in format_multipleutterances(line)
        ] + [
            '{} {}'.format(intent, line)
            for intent, lines in sorted(utterances.items()) if intent in intents
            for line in lines
        ])
    ))


def write_utterances(utterances, extutterances, intents, filename):
    with open(filename, 'w') as f:
        f.write(format_utterances(utterances, extutterances, intents).encode('utf-8'))


def main():
    args = parser.parse_args()
    parse_yaml(args.filename)


if __name__ == '__main__':
    main()
