
# Reporter

   This tool helps in gathering and formatting of data into a report. The tool
   `reporter.py` basically combines [YAML](http://yaml.org/spec/) data files
   with [Jinja2](http://jinja.pocoo.org/docs/2.10/)-based templates.  In this
   way simple markup versions of your report can be produced. Together with a
   format converter like [Pandoc](http://pandoc.org) the produced output can
   then be converted to various target formats (HTML, PDF, ...).

   To keep a good overview which data is acquired for different parts of the
   report, it is probably a good step to automate the whole workflow with a
   tool like [snakemake](https://snakemake.readthedocs.io/en/stable/) or other
   make-like tools.


# Install

   The fastest way to install datareport is to use your systems tools:

    pip install datareport

   To use the latest test version check out the test.pypi server:

    pip install --index-url https://test.pypi.org/simple datareport


## Requirements

   All required packages are listed in `environment.yaml`. In case you
   installed datareport via a package management system like pip, anaconda,
   miniconda, ... all dependencies should already be installed automatically.


# Getting Started

   For easing your first steps with datareport a small set of [documented
   examples](examples/README.md) can be found in the `examples/` folder. The
   README file gives an overview and you can find the right place to start.


## Further reading

   For designing reports you need to know about the templating language and
   since you will want to use some automation for the reporting process, also a
   make-like tool is very helpful. Look at the excellent `snakemake` for that!

   * [Jinja2](http://jinja.pocoo.org/docs/2.10/) (→ [templating
     language](http://jinja.pocoo.org/docs/2.10/templates/))

   * [Snakemake](https://pypi.org/project/snakemake/) (→ [writing
     rules](https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html))

   As data inputs you can use different formats. For understanding the details
   about each format you find a lot of information on the web, especially:

   * YAML (→ [specification](http://yaml.org/spec/)) and the
     [ruamel.yaml](https://yaml.readthedocs.io/en/latest/basicuse.html)
     package.
   * JSON (→ [specification](https://json.org/))


# Developing datareport

   Contributions are very welcome! Write issues for feature requests or
   directly file a pull-request with your contribution and/or contact me
   directly!


## Tests

   This project uses the [PyTest framework](https://docs.pytest.org/en/latest/)
   with tests defined in the [tests/](tests/) sudirectory. It is added into the
   setuptools config, so that it can be run with

    python setup.py test

   This automatically tests a temporarily packaged version.

   Alternatively you can run `pytest` manually with all it [glory
   details](https://docs.pytest.org/en/latest/usage.html).


## Releases

   The release workflow is mostly automated and is in the [release/](release/)
   folder.


