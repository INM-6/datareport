from urllib.parse import urlencode, urlunparse
from urllib.request import urlopen
import re

years = [2016, 2017, 2018]
infos = ['authors', 'publications']


def makeSearch(searchparameters, of='hx', sf='year', rg='', so='d'):
    ' creates a lambda expression to fill wildcards into a juser query URL '
    return lambda wc: urlunparse(
        [ 'https', 'juser.fz-juelich.de', '/PubExporter.py', '',
          urlencode({'of': of, 'p': searchparameters.format(wc=wc),
                     'sf': sf, 'rg':rg, 'so': so}),
          '',
        ])

rule fetchall:
    input:
        expand('juser_{info}_{year}.yaml',
            info=infos,
            year=years,
        )

rule fetch_juser:
    '''
    Do a juser query and reformat the results to yaml.
    You might need to be logged in in your browser for this to work.
    '''
    output:
        'juser_publications_{year,\d{4}}.yaml'
    params:
        search= makeSearch('cid:"I:(DE-Juel1)INM-6-20090406" AND prg:"G:(EU-Grant)720270" AND pub:"{wc.year}"'),
    shell:
        '''
        curl '{params.search}' |\
            pandoc-citeproc --bib2yaml --format=bibtex /dev/stdin |\
            cat >'{output}'
        '''
import yaml
rule fetch_authors:
    '''
    fetch all authors and their ids
    '''
    output:
        'juser_authors_{year,\d{4}}.yaml'
    params:
        search = makeSearch('cid:"I:(DE-Juel1)INM-6-20090406" AND prg:"G:(EU-Grant)720270" AND pub:"{wc.year}"', of='al'),
    run:
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

