from os.path import dirname, realpath
import json


def get_config(name):
    file_path = dirname(realpath(__file__)) + '/config/' + name + '.json'
    with open(file_path, 'r', encoding='utf-8') as fr:
        return json.loads(fr.read())
