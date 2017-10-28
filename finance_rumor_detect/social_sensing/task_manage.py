# -*- coding:utf-8 -*-

import sys
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
reload(sys)
sys.path.append("../")
from global_utils import es_user_portrait as es
#from global_config import index_manage_sensing_task,task_doc_type
from global_utils import index_sensing,type_sensing


def create_sensing_task(task):
    item = dict()
    item['task_name'] = task['task_name']
    item['social_sensors'] = task['social_sensors']
    es.index(index=index_sensing, doc_type=type_sensing, body=item)

if __name__ == "__main__":
    task=dict()
    task['task_name'] = '金融谣言识别'
    task['social_sensors'] = json.dumps(['1638782947','2258727970'])
    #create_sensing_task(task)
    es.delete(index=index_sensing,doc_type=type_sensing,id='AV9iqKe5p6BoxbAYrY0G')

    es.delete(index=index_sensing,doc_type=type_sensing,id='AV9ip2eQp6BoxbAYrY0F')
    es.delete(index=index_sensing,doc_type=type_sensing,id='AV9ipjv8p6BoxbAYrY0E')
