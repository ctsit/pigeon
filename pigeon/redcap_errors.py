from .exceptions import *

def clean_errors(error):
    err = [part.replace('\"', '') for part in error.split(',')]
    return {
        'subject': err[0].split()[0],
        'event': err[0].split()[1].replace('(', '').replace(')', ''),
        'field': err[1],
        'value': err[2],
        'message': err[3]
    }

def parse_errors(error_data):
    try:
        return [clean_errors(error) for error in error_data.split("\n") if error]
    except Exception as err:
        raise IrrecoverableError("""
        The batch you sent returned irrecoverable errors from Redcap
        The error we got from redcap was:
        {}

        The exception we encountered while trying to handle the error parsing was:
        {}

        Once you have removed ALL Protected Health information,
        please submit an issue at https://github.com/ctsit/pigeon
        """.format(error_data, str(err)))

def remove_error_fields(records, errors):
    for error in errors:
        for index, record in enumerate(records):
            subject_has_err = str(error.get('subject')) == str(record.get('dm_subjid'))
            event_has_err = error.get('event') == record.get('redcap_event_name')
            if subject_has_err and event_has_err:
                del records[index][error.get('field')]
    return records
