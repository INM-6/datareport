from urllib.parse import urlencode, urlunparse
from urllib.request import urlopen
import os.path
import re

years = [2016, 2017, 2018]
infos = ['authors', 'publications']
datadir = 'data/'

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
    return os.path.join(datadir, name.lstrip('/'))


rule Report:
    input:
        'templates/TelephoneList.md',
        phonelist= 'data/Phonelist_20170921.yaml',
        groups= 'data/HBP-groups.yaml',
        authors= 'data/juser_authors_2017.yaml',
    output:
        'TelephoneList.md'
    run:
        shell('./reporter.py -t %(template)s -o %(output)s %(datadef)s' % {
            'template': input[0],
            'datadef': " ".join(["%s=%s" % kv for kv in input.items()]),
            'output': output[0],
        })

rule fetchall:
    input:
        expand(data('juser_{info}_{year}.yaml'),
            info=infos,
            year=years,
        )

rule fetch_juser:
    '''
    Do a juser query and reformat the results to yaml.
    You might need to be logged in in your browser for this to work.
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
    fetch all authors and their ids
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