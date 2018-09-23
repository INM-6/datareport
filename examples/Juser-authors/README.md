
# Publications Example

   This example produces two different outputs from the same source.

   * A list with Author-IDs per registry
   * A list of Publications for a given year

   The actual procedure is a bit more complex, since data from different input
   datafiles is combined in each of the reports.

   Look at the Snakefile for a detailed description of each step.


## Any Year

   Note, that this example can automatically querry the external database for
   publication lists of other years. The default rule just produces a list with
   the dataset available in the example folder. The `year` is actually
   implemented as a wildcard, so you can produce lists of other years by just
   asking snakemake for them:

    '''bash
    snakemake reports_html/PublicationsList_2018.html
    '''

   It will figure out, that it needs to download some more data to build this
   target and uses `curl` to fetch it from the databases web-interface.

