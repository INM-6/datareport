#!/usr/bin/env python
# encoding: utf8
'''
Usage: reporter [options] [-y|-p|-j] [--list=<name>...] [--filter=<pyfile>...] [--template=<template>] [--output=<file>] [<datadef>...]

   Create a report by filling the template with data according to <datadef>.

   Each <datadef> must be a pair "<key>=<filename>", where key is the
   identifier used in the template and <filename> is the YAML file containing
   the corresponding data.

Options:
    -t, --template=<template>
        use an alternative template [default: report.md]

    --template-dir=<dir>
        specify the base directory for the used templates [default: .]

    --list=<name>...
        all names given in --list options will be initialized as empty list and
        consecutive `datadef`s will be appended to the list instead of assigned
        to the name. Example:

           reporter --list=bar foo=a.yml bar=b.yml bar=c.yml

        would give objects `foo` and `bar`, where `foo` represents the object
        loaded from `a.yml` and `bar` is a list containting objects loaded from
        `b.yml` and `c.yml`.

        This option can be given more than once to create multiple lists, e.g.

           reporter --list=bar --list=baz  bar=a.yml bar=b.yml baz=c.yml baz=d.yml

        would give lists `bar = [a, b]` and `baz = [c, d]`.

    --meta-dict=<name>
        change name of the metadata dictionary [default: report]

    -y, --yaml
        use yaml.load (default)

    --yaml-loader=<type>
        choose a specific loader type from the ruamel lib [default: safe]

    -j, --json
        use json.load instead of yaml.load

    -p, --python
        use eval() loading (very insecure!!!)

    -o, --output=<filename>
        write to this file instead of stdout

    --filter=<pythonfile>
        load functions from given python file and add them to the available
        filters

    -v, --verbose       increase output
    -h, --help          print this text
'''
from docopt import docopt

from pprint import pformat
import logging
from ruamel.yaml import YAML
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os.path
import shlex
import sys
import datetime
log = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def pythoneval(stream):
    return eval(stream.read())

def loadfilters(listoffiles):
    import importlib.util
    filters = dict()
    for filename in listoffiles:
        log.debug("loading filters from %s...", filename)
        spec = importlib.util.spec_from_file_location("loaded_filters", filename)
        assert spec, "Could not load python file %s" % filename
        newfilters = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(newfilters)
        for x in dir(newfilters):
            if x.startswith('_'): continue
            assert x not in filters
            filters[x] = getattr(newfilters, x)
            log.debug("   filter %s", x)
    return filters

def main(cmdline = None):
    if cmdline is None:
        cmdline = sys.argv[1:]
    else:
        cmdline = shlex.split(cmdline)  # have a possibility for testing
    args = docopt(__doc__, cmdline)

    if args['--verbose']:
        log.setLevel(logging.DEBUG)
    log.debug(pformat(args))

    log.debug("template directory '%s'", args['--template-dir'])
    env = Environment(
        loader=FileSystemLoader(args['--template-dir']),
        trim_blocks=True,
        lstrip_blocks=True,
        #autoescape=select_autoescape(['html', 'xml'])
        extensions=[
            'jinja2.ext.loopcontrols',
        ],
    )
    newfilters = loadfilters(args['--filter'])
    log.debug("new filters: %s", newfilters)
    env.filters.update(newfilters)

    # load template
    log.info("loading template '%s'...", args['--template'])
    tmpl = env.get_template(args['--template'])

    yamlin = YAML(typ=args['--yaml-loader'])
    dataloader = yamlin.load
    if args['--yaml']: dataloader = yamlin.load
    if args['--python']: dataloader = pythoneval
    if args['--json']:
        import json
        dataloader = json.load

    # load data
    data = dict()
    for datadef in args['<datadef>']:
        dataid, datafilename = datadef.split("=", 1)
        if dataid in args['--list']:
            log.info("loading '%s' entry from '%s'...", dataid, datafilename)
            data.setdefault(dataid, list()).append(dataloader(open(datafilename, 'r')))
        else:
            log.info("loading '%s' from '%s'...", dataid, datafilename)
            data[dataid] = dataloader(open(datafilename, 'r'))
    log.debug("loading data complete.")

    if args['--meta-dict'] in data:
        log.error("metadata dictionary has same name as loaded data! use '--meta-dict' to rename, or change datadef")
        return 1

    data[args['--meta-dict']] = {
        "time": datetime.datetime.now(),
    }

    # output result
    ostream = sys.stdout
    if args['--output'] is not None:
        ostream = open(args['--output'], 'w')
    log.info("writing output to %s", ostream.name)
    with ostream as outfile:
        outfile.write(tmpl.render(**data))

    return 0

if __name__ == '__main__':
    sys.exit(main())
