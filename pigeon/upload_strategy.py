import json
import datetime
from copy import copy

from pigeon.exceptions import *
import pigeon.redcap_errors as redcap_errors

class UploadStrategy(object):

    def __init__(self, strategy, api):
        """
        Strategies are
        'full'
        'batch'
        'single'
        """
        self.strategy = strategy
        self.api = api

    def __call__(self, records, report, **upload_kwargs):
        self.upload_kwargs = upload_kwargs
        uploads = {
            'full': self.__full_upload,
            'batch': self.__batch_upload,
            'single': self.__single_upload,
        }
        report.num_records_attempted = len(records)
        if report.error_correction_attempts < 3:
            return uploads[self.strategy](records, report, **upload_kwargs)
        else:
            raise Exception('Attempted to correct errors too many times')

    def __response_parse(self, res):
        status = res.status_code
        text = str(res.content, 'utf-8')
        return json.loads(text)

    def __handle_errors(self, records, data, report):
        report.error_correction_attempts += 1
        errors = redcap_errors.parse_errors(data.get('error'))
        for error in errors:
            report.errors.append(copy(error))
        report.num_of_errors += len(errors)
        records = redcap_errors.remove_error_fields(records, errors)
        return self(records, report, **self.upload_kwargs)

    def __report_fill(self, records, data, report):
        report.subjects_uploaded = sorted(list(set(data + report.subjects_uploaded)))
        report.batch_end_time.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        report.num_records_uploaded += len(records)
        report.num_subjects_uploaded += len(report.subjects_uploaded)
        report.fields_updated += sum([len(record.keys()) - 2 for record in records])
        return report

    def __full_upload(self, records, report):
        """
        Takes records and a Reporter instance
        """
        upload_data = json.dumps(records)
        res = self.api.import_records(data=upload_data)
        if (res.status_code == 403):
            raise TooManyRecords(res.content)
        data = self.__response_parse(res)
        if type(data) == type({}) and 'error' in data.keys():
            return self.__handle_errors(records, data, report)
        else:
            self.__report_fill(records, data, report)
            report.strategy_used = 'full'
            return records, report

    def __batch_upload(self, records, report, batch_size=500):
        batches = [[]]
        unfilled_batch = 0
        for record in records:
            if len(batches[unfilled_batch]) == batch_size:
                batches.append([])
                unfilled_batch += 1
            batches[unfilled_batch].append(record)
        rec_reports = [self.__full_upload(batch, report) for batch in batches]
        report.num_of_batches = len(batches)
        report.strategy_used = 'batch'
        altered_batches = [rec for rec, report in rec_reports]
        report = rec_reports[-1][1]
        return altered_batches, report

    def __single_upload(self, records, report):
        batches, report = self.__batch_upload(records, report, 1)
        report.strategy_used = 'single'
        return batches, report

