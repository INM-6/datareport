
# Minimum Example

   This example shows the absolute minimum required to build a report.
   You need

   * a template defining how the report should be structured and which data
     fields to be shown
   * a data file containing a set of values to be filled into the template

   Essentially the Snakefile then only executes one command (which you can of
   course also execute yourself):

    ../../datareport/reporter.py --template example.template.md data=keywords.yaml

   To understand the possibilities of the reporter tool, run it with `--help` option like

    ../../datareport/reporter.py --help

