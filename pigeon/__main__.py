docstr = """
Pigeon

Usage: pigeon.py [-h] (<file> <config>) [-o <output.json>]

Options:
  -h --help                                     show this message and exit
  -o <output.json> --output=<output.json>       optional output file for results

"""
import json
import datetime
from copy import copy

from docopt import docopt
import yaml
import cappy

from reporter import Reporter
from upload_strategy import UploadStrategy
from exceptions import *

_file = '<file>'
_config = '<config>'
_output = '--output'

# config file magic strings
_cv = 'cappy_version'
_tk = 'token'
_ru = 'redcap_url'
_bs = 'batch_size'

def main(args):
    with open(args[_config], 'r') as config_file:
        global config
        config = yaml.load(config_file.read())
    with open(args[_file], 'r') as infile:
        records_json = infile.read()

    api = cappy.API(config[_tk], config[_ru], config[_cv])

    report_template = {
        'num_records_attempted': 0,
        'num_subjects_uploaded': 0,
        'num_records_uploaded': 0,
        'subjects_uploaded': [],
        'errors': [],
        'datapoints_updated': 0,
        'start_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        'batch_end_time': [],
        'num_of_batches': 0,
    }

    records = json.loads(records_json)
    report.num_records_attempted = len(records)

    full_upload = UploadStrategy('full', api)

    try:
        report = Reporter(report_template)
        full_upload(records, report)
    except TooManyRecords:
        try:
            report = Reporter(report_template)
            batch_upload = UploadStrategy('batch', api)
            batch_upload(records, report, (batch_size=config[_bs] or 500))
        except:
        # do singles if irrecoverable
            pass


    print(json.dumps(batch_reports, indent=4))

def cli_run():
    args = docopt(docstr)
    main(args)

if __name__ == '__main__':
    cli_run()
    exit()
