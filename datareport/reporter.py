#!/usr/bin/env python
# encoding: utf8
'''
Usage: reporter [options] [--template=<template>] [--output=<file>] [<datadef>...]
       reporter [options] [--template=<template>] [--output=<file>] --list=<name> [<datafile>...]

   Create a report by filling the template with data according to <datadef>.

   Each <datadef> must be a pair "<key>=<filename>", where key is the
   identifier used in the template and <filename> is the YAML file containing
   the corresponding data.

Options:
    -t, --template=<template>
        use an alternative template [default: report.md]

    --template-dir=<dir>
        specify the base directory for the used templates [default: .]

    --list=<name>
        when used in the second form, all datafiles will be appended to a list
        which is assigned the name <name> [default: data]

    -j, --json
        use json.load instead of yaml.safe_load

    -p, --python
        use eval() loading (very insecure!!!)

    -o, --output=<filename>
        write to this file instead of stdout

    -v, --verbose       increase output
    -h, --help          print this text
'''
from docopt import docopt

from pprint import pformat
import logging
from ruamel import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os.path
import sys
log = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def pythoneval(stream):
    return eval(stream.read())

def main():
    args = docopt(__doc__)
    if args['--verbose']:
        log.setLevel(logging.DEBUG)
    log.debug(pformat(args))

    log.debug("template directory '%s'", args['--template-dir'])
    env = Environment(
        loader=FileSystemLoader(args['--template-dir']),
        trim_blocks=True,
        lstrip_blocks=True,
        #autoescape=select_autoescape(['html', 'xml'])
    )

    # load template
    log.info("loading template '%s'...", args['--template'])
    tmpl = env.get_template(args['--template'])

    dataloader = yaml.safe_load
    if args['--python']:
        dataloader = pythoneval
    if args['--json']:
        import json
        dataloader = json.load

    data = dict()
    for datadef in args['<datadef>']:
        dataid, datafilename = datadef.split("=", 1)
        log.info("loading '%s' from '%s'...", dataid, datafilename)
        data[dataid] = dataloader(open(datafilename, 'r'))

    for datafilename in args['<datafile>']:
        log.info("loading '%s' entry from '%s'...", args['--list'], datafilename)
        data.setdefault(args['--list'], list()).append(dataloader(open(datafilename, 'r')))
    log.debug("loading data complete.")

    ostream = sys.stdout
    if args['--output'] is not None:
        ostream = open(args['--output'], 'w')
    log.info("writing output to %s", ostream.name)
    with ostream as outfile:
        outfile.write(tmpl.render(**data))

if __name__ == '__main__':
    main()
