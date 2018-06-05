import sys
from .exceptions import *

def clean_error(error):
    err = [part.replace('\"', '') for part in error.split(',')]
    return {
        'subject': err[0].split()[0],
        'event': err[0].split()[1].replace('(', '').replace(')', ''),
        'field': err[1],
        'value': err[2],
        'message': err[3]
    }

def parse_errors(error_data):
    print(error_data, file=sys.stderr)
    if 'There were errors with your request.' in error_data:
        raise IrrecoverableError(error_data)
    if 'data being misformatted' in error_data:
        raise IrrecoverableError(error_data)
    return [clean_error(error) for error in error_data.split("\n") if error]

def remove_error_fields(records, errors):
    for error in errors:
        for index, record in enumerate(records):
            subject_has_err = str(error.get('subject')) == str(record.get('dm_subjid'))
            event_has_err = error.get('event') == record.get('redcap_event_name')
            if subject_has_err and event_has_err:
                del records[index][error.get('field')]
    return records
