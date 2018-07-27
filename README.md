
# Reporter

   This tool helps in gathering and formatting of data into a report. The tool
   `reporter.py` basically combines YAML data files with Jinja2-based
   templates.  In this way simple markup versions of your report can be
   produced. Together with a format converter like [Pandoc](http://pandoc.org)
   the produced output can then be converted to various target formats (HTML,
   PDF, ...).

   To keep a good overview which data is aquired for different parts of the
   report, it is probably a good step to automate the whole workflow with a
   tool like [snakemake](https://snakemake.readthedocs.io/en/stable/) or other
   make-like tools.


# Install

   The fastest way to install datareport is to use your systems tools:

    pip install datareport

   To use the latest test version check out the test.pypi server:

    pip install --index-url https://test.pypi.org/simple datareport

   Currently no executable is installed, but you can set an alias in your bash
   with

    alias reporter='python -c "from datareport import reporter; reporter.main()"'

   If you want to have this permanently configured, just paste this line into
   your `.bashrc` (or equivalent).

## Requirements

   All required packages are listed in `environment.yaml`. In case you
   installed datareport via a package management system like pip, anaconda,
   miniconda, ... all dependencies should already be installed automatically.


# Getting Started

   For easing your first steps with datareport a small set of documented
   examples can be found in the `examples/` folder. The README file gives an
   overview and you can find the right place to start.

