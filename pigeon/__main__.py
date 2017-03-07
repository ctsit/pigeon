"""
Pigeon

Usage: pigeon.py [-h] (<file> <config>) [-o <output.json>]

Options:
  -h --help                                     show this message and exit
  -o <output.json> --output=<output.json>       optional output file for results

"""
import json

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

def main(args):
    with open(args[_config], 'r') as config_file:
        global config
        config = yaml.load(config_file.read())
    with open(args[record_file], 'r') as infile:
        records_json = infile.read()
    api = cappy.API(config[_tk], config[_ru], config[_cv])

    try:
        response = api.import_records(data=records_json)
        if not response.status_code == 200:
            raise Exception
        print(response)
        print(response.content)
    except Exception as err:
        print(err)
        print("Couldn't send all records, sending one at a time")
        records = json.loads(records_json)
        for record in records:
            single = json.dumps([record])
            try:
                response = api.import_records(data=single)
                print(response)
                print(response.content)
            except:
                print('Something went very wrong')


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
    exit()
