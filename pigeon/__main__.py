docstr = """
Pigeon

Usage: pigeon.py [-h] (<file> <config>) [-o <output.json>]

Options:
  -h --help                                     show this message and exit
  -v --version                                  show version
  -o <output.json> --output=<output.json>       optional output file for results

"""
import json
import datetime
from copy import copy

from docopt import docopt
import yaml
import cappy

from .reporter import Reporter
from .upload_strategy import UploadStrategy
from .exceptions import *
from .risk_manager import RiskManager
from pigeon.version import __version__

_file = '<file>'
_config = '<config>'
_output = '--output'

# config file magic strings
_cv = 'cappy_version'
_tk = 'token'
_ru = 'redcap_url'
_ro = 'requests_options'
_bs = 'batch_size'

def main():
    args = docopt(docstr, version=__version__)
    with open(args[_config], 'r') as config_file:
        global config
        config = yaml.load(config_file.read())
    with open(args[_file], 'r') as infile:
        records_json = infile.read()

    api = cappy.API(config[_tk], config[_ru], config[_cv], requests_options=config.get(_ro))

    report_template = {
        'file_loaded': args[_file],
        'num_records_attempted': 0,
        'num_subjects_uploaded': 0,
        'num_records_uploaded': 0,
        'num_of_errors': 0,
        'subjects_uploaded': [],
        'errors': [],
        'error_correction_attempts': 0,
        'fields_updated': 0,
        'start_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        'batch_end_time': [],
        'num_of_batches': 1,
        'strategy_used': "",
    }

    records = json.loads(records_json)
    report = Reporter('pigeon_v1', report_template)
    full_upload = UploadStrategy('full', api)
    batch_upload = UploadStrategy('batch', api)
    single_upload = UploadStrategy('single', api)

    upload = RiskManager(lambda : full_upload(records, report))
    upload.add_backup(lambda ex: batch_upload(records, report.reset().add_key_value('full_ex', ex)))
    upload.add_backup(lambda ex: single_upload(records, report.reset().add_key_value('batch_ex', ex)))

    result, ran_out_of_plans = upload()

    if ran_out_of_plans:
        report.add_key_value('exceptions', [ex for ex in upload.exceptions_encountered])

    print(report.serialize())

if __name__ == '__main__':
    main()
    exit()
