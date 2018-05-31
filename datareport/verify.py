#!/usr/bin/env python
# encoding: utf8
'''
Usage: verify [options] <filename>

Options:
    --validation=<rules>
        validation definition file in YAML format
        [default: verify.yaml]

    -h, --help      print this help text
    -v, --verbose   give more details about the processing
'''

from docopt import docopt
import logging
from ruamel import yaml
import re

log = logging.getLogger()
logging.basicConfig(level=100) #logging.INFO)

def check(condition, warning_if_false, level=logging.WARNING):
    log.debug("check for '%s'", warning_if_false)
    if not condition:
        if level > logging.WARNING:
            raise AssertionError(warning_if_false)
        log.log(level, warning_if_false)

class Validator(object):
    def __init__(self, rulefile=None, rules=None, throw=False):
        '''
        Initialize the validator with given `rules` or rules loaded from given
        YAML `rulefile`.

        If parameter `throw` is `True`, then validate() will raise an
        AssertionError with additional information instead of True or False.
        '''
        self.throw = throw
        self.rules = rules
        if rulefile is not None:
            log.debug("opening %s...", rulefile)
            with open(rulefile, 'r') as infile:
                self.rules = yaml.safe_load(infile)

    def validate_file(self, filename):
        '''
        Try to load yaml from the file with given name and run its data through validate

        returns the result of validate()
        '''
        log.debug("opening %s...", filename)
        data = None
        with open(filename, 'r') as infile:
            data = yaml.safe_load(infile)
        return self.validate(data)

    def _validate_dict(self, item, rules, path):
        '''
        Validate a dict item. Optional key `regex` can be used to verify the
        content of the string

        >>> v = Validator(rules={'type': 'dict',
        ...                      "keys": {'type': 'str', 'regex':r'\w+'},
        ...                      "values": {'type': 'int', 'min': 0},
        ...                     }
        ...              )
        >>> v.validate({"a", 42})
        False
        >>> v.validate({"a": 42})
        True
        >>> v.validate({"a 4": 42})
        False
        >>> v.validate({"b": "42"})
        False
        >>> v.validate({"4": -42})
        False
        '''
        assert isinstance(item, dict), "%s: expected dict, got %s!" % (":".join(path), type(item).__name__)
        checktype = "dict"
        if "keys" in rules:
            log.debug("assert correct type of keys of %s...", ":".join(path))
            for k in item.keys():
                assert self.validate(k, rules['keys'], path+[str(k)])
        if "values" in rules:
            log.debug("assert correct values of %s: %s", ":".join(path), checktype)
            for v in item.values():
                assert self.validate(v, rules['values'], path+["values", str(v)])
        return True

    def _validate_str(self, item, rules, path):
        '''
        Validate a string item. Optional key `regex` can be used to verify the
        content of the string

        >>> v = Validator(rules={'type': 'str'})
        >>> v.validate("1")
        True
        >>> v.validate(1)
        False
        >>> v = Validator(rules={'type': 'str', 'regex':r'\d+\s?units'})
        >>> v.validate("23 units")
        True
        >>> v.validate("unit 23")
        False
        '''
        assert isinstance(item, str), "%s: expected str, got %s!" % (":".join(path), type(item).__name__)
        if "regex" in rules:
            assert re.fullmatch(rules['regex'], item, rules.get('regex_flags', 0)), "%s INVALID" % ":".join(path)
        return True

    def _validate_int(self, item, rules, path):
        '''
        Validate an integer.

        Optional keys 'min' and 'max' can be used to limit allowed values. The
        range is inclusive `[min, max]`. The optional keys 'sup', 'inf' can be
        used for the exclusive range checks `(inf, sup)`. Range can be mixed
        `[min, sup)`. Range checks are independant, so empty ranges (min=1,
        max=0) are possible.

        >>> v = Validator(rules={'type': 'int'})
        >>> v.validate(1)
        True
        >>> v.validate(3.1415)
        False
        >>> v = Validator(rules={'type': 'int', 'min':42, 'sup':43})
        >>> v.validate(41)
        False
        >>> v.validate(42)
        True
        >>> v.validate(43)
        False
        >>> v = Validator(rules={'type': 'int', 'inf':41, 'max':42})
        >>> v.validate(41)
        False
        >>> v.validate(42)
        True
        >>> v.validate(43)
        False
        '''
        assert isinstance(item, int), "%s: expected int, got %s!" % (":".join(path), type(item).__name__)
        if "min" in rules:
            assert item >= rules['min']
        if "inf" in rules:
            assert item > rules['inf']
        if "sup" in rules:
            assert item < rules['sup']
        if "max" in rules:
            assert item <= rules['max']
        return True

    def _validate_float(self, item, rules, path):
        '''
        Validate a floating point number.

        Optional keys 'min' and 'max' can be used to limit allowed values. The
        range is inclusive `[min, max]`. The optional keys 'sup', 'inf' can be
        used for the exclusive range checks `(inf, sup)`. Range can be mixed
        `[min, sup)`. Range checks are independant, so empty ranges (min=1,
        max=0) are possible.

        >>> v = Validator(rules={'type': 'float'})
        >>> v.validate(1)
        False
        >>> v.validate(3.1415)
        True
        >>> v = Validator(rules={'type': 'float', 'min':42, 'sup':43})
        >>> v.validate(41.)
        False
        >>> v.validate(42.)
        True
        >>> v.validate(43.)
        False
        >>> v = Validator(rules={'type': 'float', 'inf':41, 'max':42})
        >>> v.validate(41.)
        False
        >>> v.validate(42.)
        True
        >>> v.validate(43.)
        False
        '''
        assert isinstance(item, float), "%s: expected float got %s!" % (":".join(path), type(item).__name__)
        if "min" in rules:
            assert item >= rules['min']
        if "inf" in rules:
            assert item > rules['inf']
        if "sup" in rules:
            assert item < rules['sup']
        if "max" in rules:
            assert item <= rules['max']
        return True

    def _validate_in(self, item, rules, path):
        '''
        Branch validation to satisfy any of a given list of rules

        >>> v = Validator(rules={'type': 'in',
        ...                      'values': [{'type': 'int', 'min': 23},
        ...                                 {'type': 'float', 'max': 1.0},
        ...              ]})
        >>> v.validate(1)
        False
        >>> v.validate(1.0)
        True
        >>> v.validate(42)
        True
        >>> v.validate(42.0)
        False
        '''
        ###
        ### NOTE: Since this is an idirect validation calling self.validate()
        ### the result must be asserted in order to be independant of self.throw.
        ###
        checkers = rules['values']
        assert isinstance(checkers, list), "checker of type 'in' must have 'values'"
        for rule in checkers:
            try:
                assert self.validate(item, rule, path)
                return True
            except AssertionError:
                pass
        assert False, "%s: got %s, expected %s" % (":".join(path), type(item).__name__, str(rules))

    def _validate_list(self, item, rules, path):
        '''
        >>> v = Validator(rules={'type': 'list'})
        >>> v.validate([1,2,3])
        True
        >>> v.validate("str")
        False
        >>> v = Validator(rules={'type': 'list', "values": {'type': "int"}})
        >>> v.validate([1,2,3])
        True
        >>> v.validate([1,'str',3])
        False
        '''
        assert isinstance(item, list), "%s: expected list, got %s!" % (":".join(path), type(item).__name__)
        if "values" in rules:
            for i, subitem in enumerate(item):
                assert self.validate(subitem, rules['values'], path+[str(i)])
        return True

    def _validate_dictdescent(self, item, rules, path):
        '''
        >>> v = Validator(rules={'type': 'dictdescent'})
        >>> v.validate([1,2,3])
        False
        >>> v = Validator(rules={'type': 'list', "values": {'type': "int"}})
        >>> v.validate([1,2,3])
        True
        >>> v.validate([1,'str',3])
        False
        '''
        assert isinstance(item, dict), "%s: expected dict, got %s!" % (":".join(path), type(item).__name__)
        if "mandatory" in rules:
            assert all([key in item for key in rules['mandatory']]), "%s: misses mandatory keys" % (":".join(path))
        #if "allowed" in rules:
        #   good
        if "deprecated" in rules:
            for key in rules['deprecated'].keys():
                if key in item:
                    log.warning("%s: deprecated key %s", ":".join(path), key)
        if "forbidden" in rules:
            assert not any([key in item for key in rules['forbidden'].keys()]), "%s: has forbidden keys" % (":".join(path))

        otherkeys = [key for key in item.keys() if not any([key in rules.get(good, {}) for good in ['mandatory', 'allowed', 'deprecated']])]
        assert rules.get("others-allowed", False) or not any(otherkeys), "%s: there are keys that are addtional keys %s and others-allowed is False" % (":".join(path), repr(otherkeys))

        return True

    def validate(self, tree, rules=None, path=['/']):
        '''
        Validate the object `tree` according to given rules. By default, if no
        rules are given, the rule base loaded during the construction of the
        validator is used.

        >>> v = Validator(rules={'type': 'list'}, throw=False)
        >>> v.validate(123)
        False
        >>> v = Validator(rules={'type': 'list'}, throw=True)
        >>> v.validate(123)
        Traceback (most recent call last):
            ...
        AssertionError: /: expected list, got int!
        '''
        if rules is None: rules = self.rules
        if not isinstance(rules, dict):
            print("rules = %s", repr(rules))
            assert False, "rule must be of type dict, but is %s" % repr(rules)
        checktype = rules.get('type')
        try:
            check = getattr(self, "_validate_"+checktype)
        except Exception:
            log.error("no validator of type '%s'", checktype)
            raise
        try:
            log.debug("assert correct type %s: %s", ":".join(path), checktype)
            assert check(tree, rules, path), "validation of %s failed!" % checktype
        except AssertionError as e:
            log.error("%s IS INVALID: %s", ":".join(path), e)
            if self.throw:
                raise
            return False
        log.debug("%s validated as %s", ":".join(path), checktype)
        return True

if __name__ == '__main__':
    args = docopt(__doc__)
    if args['--verbose']:
        log.setLevel(logging.DEBUG)

    validator = Validator(rulefile = args['--validation'])

    valid = validator.validate_file(args['<filename>'])
    if valid:
        print("valid.")
    else:
        print("INVALID!")

