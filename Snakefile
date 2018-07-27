from urllib.parse import urlencode, urlunparse
from urllib.request import urlopen
import os.path
import re

configfile: 'config.yaml'

def makeSearch(searchparameters, of='hx', sf='year', rg='', so='d'):
    ' creates a lambda expression to fill wildcards into a juser query URL '
    return lambda wc: urlunparse(
        [ 'https', 'juser.fz-juelich.de', '/PubExporter.py', '',
          urlencode({'of': of, 'p': searchparameters.format(wc=wc),
                     'sf': sf, 'rg':rg, 'so': so}),
          '',
        ])

def data(name):
    ' returns a full filename to the datafile with given name '
    return os.path.join(config['datadir'], name.lstrip('/'))

def report(name):
    return os.path.join(config['outdir'], name.lstrip('/'))

def report_html(name):
    return os.path.join(config['outdir_html'], name.lstrip('/'))


rule all:
    input:
        report_html('AuthorList.html'),
        report_html('TelephoneList.html'),
        report_html('PublicationsList_2017.html'),
        report_html('IT-Inventory.html'),
        report_html('examples.html'),


rule mkhtml:
    input:
        files=[report('{name}.md')],
        css='document.css',
    output:
        report_html('{name}.html'),
    shell:
        '''
        pandoc -f markdown+simple_tables+multiline_tables -t html --css {input.css} -o {output} {input.files}
        '''


rule AuthorList:
    '''
    This rule renders the authors database into a nicely formatted MARKDOWN file
    '''
    input:
        'templates/AuthorList.md',
        list= 'data/juser_authors_2017.yaml',
    output:
        report('AuthorList.md')
    run:
        shell('./datareport/reporter.py -t %(template)s -o %(output)s %(datadef)s' % {
            'template': input[0],
            'datadef': " ".join(["%s=%s" % kv for kv in input.items()]),
            'output': output[0],
        })


rule IT_inventory:
    input:
        'templates/IT-Inventory.md',
        data=os.path.expanduser('~/sdvlp/edvdata/edvdata.yaml'),
    output:
        report('IT-Inventory.md')
    run:
        shell('./datareport/reporter.py -t %(template)s -o %(output)s %(datadef)s' % {
            'template': input[0],
            'datadef': " ".join(["%s=%s" % kv for kv in input.items()]),
            'output': output[0],
        })


rule TelephoneList:
    '''
    output: MARKDOWN file
    '''
    input:
        'templates/TelephoneList.md',
        phonelist = 'data/Phonelist_20170921.yaml',
    output:
        report('TelephoneList.md')
    run:
        shell('./datareport/reporter.py -t %(template)s -o %(output)s %(datadef)s' % {
            'template': input[0],
            'datadef': " ".join(["%s=%s" % kv for kv in input.items()]),
            'output': output[0],
        })

rule examples:
    '''
    output: MARKDOWN file
    '''
    input:
        'templates/examples.md',
        data = 'data/keywords.yaml',
    output:
        report('examples.md')
    run:
        shell('./datareport/reporter.py -t %(template)s -o %(output)s %(datadef)s' % {
            'template': input[0],
            'datadef': " ".join(["%s=%s" % kv for kv in input.items()]),
            'output': output[0],
        })

rule PublicationsList:
    '''
    output: MARKDOWN file
    '''
    input:
        'templates/PublicationsList.md',
        groups = 'data/HBP-groups.yaml',
        authors = 'data/juser_authors_{year}.yaml',
        publications = 'data/juser_publications_{year}.yaml',
    output:
        report('PublicationsList_{year}.md')
    run:
        shell('./datareport/reporter.py -t %(template)s -o %(output)s %(datadef)s' % {
            'template': input[0],
            'datadef': " ".join(["%s=%s" % kv for kv in input.items()]),
            'output': output[0],
        })


rule fetchall:
    input:
        expand(data('juser_{info}_{year}.yaml'),
            info=config['infos'],
            year=config['years'],
        )

rule fetch_juser:
    '''
    Do a juser query and reformat the results to yaml.
    You might need to be logged in in your browser for this to work.

    output: YAML file
    '''
    output:
        data('juser_publications_{year,\d{4}}.yaml')
    params:
        search= makeSearch('cid:"I:(DE-Juel1)INM-6-20090406" AND prg:"G:(EU-Grant)720270" AND pub:"{wc.year}"'),
    shell:
        '''
        curl '{params.search}' |\
            pandoc-citeproc --bib2yaml --format=bibtex /dev/stdin |\
            cat >'{output}'
        '''
rule fetch_authors:
    '''
    fetch all authors and their ids from the Juser database. You need to have access to the relevant data, of course.

    output: YAML file
    '''
    output:
        data('juser_authors_{year,\d{4}}.yaml')
    params:
        search = makeSearch('cid:"I:(DE-Juel1)INM-6-20090406" AND prg:"G:(EU-Grant)720270" AND pub:"{wc.year}"', of='al'),
    run:
        from ruamel import yaml
        authors = dict()
        infos = re.compile(r'(?P<family>[^,\[]+),? ?(?P<given>[^\[]*) \[P:\((?P<registry>[^)]+)\)(?P<id>[^\]]+)\]')
        with urlopen(params.search) as infile:
            for line in infile:
                for author in line.decode("utf8").split(";"):
                    match = infos.match(author.strip())
                    if match is None:
                        print("Offending line: "+author)
                    else:
                        alt = authors.setdefault("{family}, {given}".format(**match.groupdict()), list())
                        data = dict(match.groupdict())
                        if data not in alt:
                            alt.append(data)
        yaml.dump(authors, open(output[0], 'w'))



rule csv2yaml:
    input:
        '{name}.csv'
    output:
        '{name}.yaml'
    run:
        from ruamel import yaml
        import csv
        with open(input[0], 'r') as infile, open(output[0], 'w') as outfile:
            csvinput = csv.reader(infile)
            head = None
            data = list()
            for row in csvinput:
                if head is None:
                    head = row
                    continue
                data.append(dict(zip(head, row)))
            yaml.dump(data, stream=outfile)


rule upload:
    input:
        'dist/datareport-0.1.2.tar.gz'
    params:
        repo = "testpypi"
    shell:
        '''
        twine upload --repository {params.repo} {input}
        '''


rule package:
    input:
        'datareport/',
    output:
        'dist/datareport-0.1.2.tar.gz'
    shell:
        '''
        python setup.py sdist
        '''


rule test:
    input:
        'test.verify.done'

rule test_verify:
    input:
        prog='datareport/verify.py',
        data=['tests/verify.yaml']*2,
    output:
        temporary(touch('test.verify.done')),
    shell:
        '''
        ./{input.prog} --validation {input.data}
        '''
