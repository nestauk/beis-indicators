#!/usr/bin/env python

import click
from collections import defaultdict
from datetime import datetime
import json
import os
import yaml


from beis_indicators import project_dir


@click.command()
@click.option('--test', type=bool, help='Output test readme', default=True)
def generate(test):
    processed_dir = f'{project_dir}/data/processed/'

    header = generate_header_text()
    indicators = generate_indicator_text(processed_dir)

    text = header + indicators

    if test:
        fout = f'{processed_dir}/README_test.md'
    else:
        fout = f'{processed_dir}/README.md'

    with open(fout, 'w') as f:
        f.write(text)

def generate_indicator_text(processed_dir):
    schema_groups = {}
    framework = load_framework()
    for group in framework:
        schema_groups[group['id']] = []

    framework_labels = {f['id']: f['label'] for f in framework} 

    subdirs = list_subdirs(processed_dir)
    for subdir in subdirs:
        files = os.listdir(subdir)
        schema_dirs = [os.path.join(subdir, f) for f in files if f[-4:] == 'yaml']
        for schema in schema_dirs:
            schema_md, framework_group = generate_dataset_entry(schema)
            schema_groups[framework_group].append(schema_md)
    
    md = ''
    for k, group in schema_groups.items():
        md = md + f'## {framework_labels[k]}\n'
        for indicator in group:
            md = md + indicator + '\n'
    return md

def generate_header_text():
    now = time_now()
    header = (
            f'# Processed Indicators\n'

            'This folder contains datasets for processed indicators. Each '
            'sub folder is identified by the data source (e.g. Eurostat) and '
            'contains the indicators obtained from that source. Every '
            'indicator is stored a separate file (.csv) and is accompanied '
            'by a schema (.yaml) which describes the dataset and the fields.\n\n'

            'Each indicator csv contains four columns, with each row '
            'representing the indicator value for a specific region and point '
            'in time. The fields are:\n\n'
            
            '- `year`: the year for this indicator value\n'
            '- `<region_id>`: the code of the region for this indicator value '
            'e.g. UKI1'
            '- `<region_year_spec>`: the version of the regions being used for '
            'for this indicator value e.g. NUTS 2016\n'
            '- `<value>`: abbreviated name of the indicator\n\n'

            'The full set of available indicators is listed below.\n\n'
            f'Last updated: {now}\n\n'
            )
    return header

def time_now():
    now = datetime.utcnow()
    now = datetime.strftime(now, format='%D')
    return now + ' UTC'

def load_framework():
    '''load_framework
    Loads json that stores framework information.
    '''
    framework_fin = f'{project_dir}/data/aux/framework.json'
    with open(framework_fin, 'r') as f:
        framework = json.load(f)
    return framework

def parse_schema(schema):
    '''parse_schema
    Extracts, formats and returns field content for each indicator entry in 
    readme.
    '''
    readme_fields = dict(
        title=schema['schema']['value']['description'],
        source=schema['source_name'],
        years=parse_year_range(schema['year_range']),
        long_description=schema['description'],
        experimental=parse_experimental(schema['is_experimental'])
        )
    return readme_fields

def generate_indicator_link(dir, schema):
    base_url = ('https://raw.githubusercontent.com/nestauk/beis-indicators'
                '/dev/data/processed/{}/{}.csv')

    source = dir.split('/')[-2]
    field_name = schema['schema']['value']['id']
    return base_url.format(source, field_name)

def generate_dataset_entry(schema_dir):
    with open(schema_dir, 'r') as f:
        schema = yaml.safe_load(f.read())

    framework_group = schema['framework_group']
    link = generate_indicator_link(schema_dir, schema)

    fields = parse_schema(schema)
    dataset_entry = (
            f"### {fields['title']}\n"
            f"- **Description:** {fields['long_description']}\n"
            f"- **Source:** {fields['source']}\n"
            f"- **Years Available:** {fields['years']}\n"
            f"- **Experimental:** {fields['experimental']}\n"
            f"- [Download]({link})\n\n"
            )
    return dataset_entry, framework_group

def parse_year_range(years):
    return f'{years[0]} - {years[1]}'

def parse_experimental(experimental):
    if True:
        return 'Yes'
    else:
        return 'No'

def list_subdirs(dir):
    '''list_subdirs
    Returns a list of sub directory names that exist within dir.
    '''
    paths = [os.path.join(dir, p) for p in os.listdir(dir)]
    subdirs = [p for p in paths if os.path.isdir(p)]
    return subdirs

if __name__ == "__main__":
    generate()
