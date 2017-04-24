import json
import datetime

from exceptions import *
import redcap_errors


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

    def __call__(self, records, report, **upload_specific_kwargs):
        uploads = {
            'full': self.__full_upload,
            'batch': self.__batch_upload,
            'single': self.__single_upload,
        }
        return uploads[self.strategy](records, report, **upload_specific_kwargs)

    def __response_parse(self, res):
        status = res.status_code
        text = str(res.content, 'utf-8')
        try:
            data = json.loads(text)
        except:
            data = text
        return status, data

    def __handle_errors(self, records, data, report):
        errors = redcap_errors.parse_errors(data.get('error'))
        for error in errors:
            report['errors'].append(copy(error))
        records = redcap_errors.remove_error_fields(records, errors)
        return self.__full_upload(records, report)

    def __full_upload_report_fill(self, records, data, report):
        report.subjects_uploaded = list(set(data + report.subjects_uploaded))
        report.batch_end_time.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        report.num_records_uploaded += len(data)
        report.num_subjects_uploaded = len(report.subjects_uploaded)
        report.datapoints_updated += sum([len(record.keys()) - 2 for record in records])
        return report

    def __full_upload(self, records, report):
        """
        Takes json records and a Reporter instance
        """
        res = api.import_records(data=records)
        status, data = self.__response_parse(res)
        if status == 403:
            raise TooManyRecords('You are trying to upload too many records.')
        elif 'error' in data.keys():
            return self.__handle_errors(records, data, report)
        else:
            return self.__full_upload_report_fill(records, data, report)

    def __batch_upload(self, records, report, batch_size=500):
        batches = [[]]
        unfilled_batch = 0
        for record in records:
            if len(batches[unfilled_batch] == batch_size):
                batches.append([])
                unfilled_batch += 1
            batches[unfilled_batch].append(record)
        for batch in batches:
            report = self.__full_upload(batch, report)
        report.num_of_batches = len(batches)
        return report

    def __single_upload(self, records, report):
        return self.__batch_upload(records, report, 1)

