
# Release Process

   The current release is configured in `config.yaml`. This is the version that
   will be built.

   To create a test release and upload it to the pypi test server run

    $ snakemake

   For a full release run

    $ snakemake release

   If you only want to create the package run

    $ snakemake package


