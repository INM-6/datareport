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

