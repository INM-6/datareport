
Reporter
--------

This workflow shows the gathering and formatting of data into a report. The
tool `reporter.py` basically combines YAML data files with Jinja2-based
templates. Together with a format converter like pandoc the produced output
can be readable Markdown to HTML, PDF, etc.


Install
-------

   pip install --index-url https://test.pypi.org/simple datareport

   alias reporter='python -c "from datareport import reporter; reporter.main()"'
