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


_file = '<file>'
_config = '<config>'
_output = '--output'

# config file magic strings
_cv = 'cappy_version'
_tk = 'token'
_ru = 'redcap_url'
_bs = 'batch_size'

def batchify(records, batch_size=0):
    if batch_size:
        batched = [[]]
        curr_batch = 0
        for record in records:
            if len(batched[curr_batch]) >= batch_size:
                batched.append([])
                curr_batch += 1
            batched[curr_batch].append(record)
    return batched

def parse_errors(errors):
    # if is that one error we always see
    # 'There were errors with your request. If you are sending data, then it might be due to the data being misformatted'
    ## kick them out to the singles
    # else
    ## parse the errors and get the error dicts
    pass

def upload_singles(api, records, report):
    for record in records:
        res = api.import_records(data=json.dumps([record]))
        data = json.loads(str(res.content, 'utf-8'))
        # add information to the report

def upload(api, records, report):
    response = api.import_records(data=json.dumps(records))
    data = json.loads(str(response.content, 'utf-8'))
    if type(data) == type({}) and data.get('error'):
        errors = data.get('error').split('\n')
        err_dicts = parse_errors(errors)
        if not len(err_dicts):
            upload_singles(api, records, report)
        else:
            report['errors'] = err_dicts
            for error in err_dicts:
                for index, record in enumerate(records):
                    subject_has_err = str(error.get('subject')) == str(record.get('dm_subjid'))
                    event_has_err = error.get('event') == record.get('redcap_event_name')
                    if subject_has_err and event_has_err:
                        del records[index][error.get('field')]
            response = api.import_records(data=json.dumps(records))

        report['subjects_uploaded'] = [str(item) for item in json.loads(str(response.content, 'utf-8'))]
        report['subjects_uploaded'].sort()
        report['num_subjects_uploaded'] = len(report['subjects_uploaded'])
        report['end_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        for subj_ev in records:
            for key in subj_ev:
                report['datapoints_updated'] += 1

def main(args):
    with open(args[_config], 'r') as config_file:
        global config
        config = yaml.load(config_file.read())
    with open(args[_file], 'r') as infile:
        records_json = infile.read()
    api = cappy.API(config[_tk], config[_ru], config[_cv])

    reports = [{
        'num_subjects_uploaded': 0,
        'subjects_uploaded': [],
        'errors': [],
        'datapoints_updated': 0,
        'start_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        'end_time': None
    }]

    records = json.loads(records_json)
    batched = [records]
    response = api.import_records(data=records_json)

    if response.status_code != 403:
        data = json.loads(str(response.content, 'utf-8'))
    else:
        print('This is redcap\'s way of saying that there are too many records')
        print(response)
        print(response.content)
        batched = batchify(records, config[_bs])

    batch_reports = [copy(reports[0]) for item in range(0,len(batched))]

    zipped = zip(batched, batch_reports)
    for pair in zipped:
        upload(api, pair[0], pair[1])

    print(json.dumps(batch_reports, indent=4))

def clean_err(err):
    return {
        'subject': err[0].split()[0].replace('"', ''),
        'event': err[0].split()[1].replace('(', '').replace(')', '').replace('"',''),
        'field': err[1].replace('"',''),
        'value': err[2].replace('"',''),
        'message': err[3].replace('"','')
    }

def cli_run():
    args = docopt(docstr)
    main(args)

if __name__ == '__main__':
    cli_run()
    exit()
