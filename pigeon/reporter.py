from copy import copy
import json

class Reporter(object):

    def __init__(self, source, output_dict):
        self.__template = {}
        self.__source = source
        for key, value in output_dict.items():
            self.add_key_value(key, value)

    def serialize(self, sort_keys=True, indent=4):
        acc = {
            'source': self.__source,
            'output': {}
        }
        for key in self.__template.keys():
            acc['output'][key] = getattr(self, key)
        return json.dumps(copy(acc), sort_keys=sort_keys, indent=indent)

    def add_key_value(self, key, value):
        key_copy = copy(key)
        value_copy = copy(value)
        self.__template[key_copy] = value_copy
        setattr(self, key_copy, value_copy)

    def get_template(self):
        return copy(self.__template)

