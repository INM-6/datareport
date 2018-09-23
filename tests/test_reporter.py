from datareport.reporter import main as reporter
import sys, os
import pytest
import shlex
import re

def test_help():
    # check if the -h flag correctly exits
    with pytest.raises(SystemExit):
        sys.argv.append('-h')
        reporter();

def test_simple(tmpdir):
    # check if a default template can be rendered
    template = tmpdir.join("report.md")
    template.write("# Hello World")
    assert template.check()
    output = tmpdir.join("output.md")
    reporter("-v --template-dir '%s' -o '%s'" % (tmpdir, output));
    assert output.check()
    assert output.read() == "# Hello World"

def test_date(tmpdir):
    # check if the metadata contains the 'time' field
    template = tmpdir.join("report.md")
    template.write("# Hello World {{ report.time.date() }}")

    output = tmpdir.join("output.md")
    reporter("-v --template-dir '%s' -o '%s'" % (tmpdir, output));
    assert output.check()
    assert re.match(
        r'# Hello World 2\d{3}-\d\d-\d\d',
        output.read()
        )

def test_yamldata(tmpdir):
    # check if simple yaml data can correctly be loaded
    template = tmpdir.join("report.md")
    template.write("# Hello {{ data.name }}")

    yaml = tmpdir.join("data.yaml")
    yaml.write("name: World")
    assert yaml.check()
    output = tmpdir.join("output.md")
    reporter("-v --template-dir '%s' data=%s -o '%s'" % (tmpdir, yaml, output));
    assert output.check()
    assert re.match(
        r'# Hello World',
        output.read()
        )


def test_insufficient_data(tmpdir):
    # check if it breaks when a datadef is missing
    template = tmpdir.join("report.md")
    template.write("# Hello {{ data.name }}")

    output = tmpdir.join("output.md")
    #with pytest.raises(ValueError):
    reporter("-v --template-dir '%s' -o '%s'" % (tmpdir, output))
    assert False ## this test passes and it shouldn't
    #expecting
    #
    # DEBUG:root:template directory '.'
    # INFO:root:loading template 'report.md'...
    # DEBUG:root:loading data complete.
    # INFO:root:writing output to <stdout>
    # Traceback (most recent call last):
    #   File "../datareport/reporter.py", line 138, in <module>
    #     sys.exit(main())
    #   File "../datareport/reporter.py", line 133, in main
    #     outfile.write(tmpl.render(**data))
    #   File "/home/terhorst/miniconda3/envs/datareport/lib/python3.6/site-packages/jinja2/asyncsupport.py", line 76, in render
    #     return original_render(self, *args, **kwargs)
    #   File "/home/terhorst/miniconda3/envs/datareport/lib/python3.6/site-packages/jinja2/environment.py", line 1008, in render
    #     return self.environment.handle_exception(exc_info, True)
    #   File "/home/terhorst/miniconda3/envs/datareport/lib/python3.6/site-packages/jinja2/environment.py", line 780, in handle_exception
    #     reraise(exc_type, exc_value, tb)
    #   File "/home/terhorst/miniconda3/envs/datareport/lib/python3.6/site-packages/jinja2/_compat.py", line 37, in reraise
    #     raise value.with_traceback(tb)
    #   File "./report.md", line 1, in top-level template code
    #     # Hello {{ data.name }}
    #   File "/home/terhorst/miniconda3/envs/datareport/lib/python3.6/site-packages/jinja2/environment.py", line 430, in getattr
    #     return getattr(obj, attribute)
    # jinja2.exceptions.UndefinedError: 'data' is undefined

    assert not output.check()   # no output should have been produced
