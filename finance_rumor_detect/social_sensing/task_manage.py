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
    sensors = ['1638782947','2000961721','1974561081','1988800805','1801487174',\
                '1752549400','2972154552','6354818270','6279793619','1704103183',\
                '1649470535','2397130344','2397130344','2810373291','2286908003',\
                '1774800467','2649363891','1776830283','1315587597','1905628462',\
                '1664176597','2311077472','1702925432','1641561812','1649173367',\
                '1393100891','1650111241','1838672663','1865425867','1741543435',\
                '1663937380','1642088277','1733583753','1708922835','1193725273',\
                '1657236125','1615813834','1649252577','1642482194','1642732730',\
                '1648948823','1649159940','1698233740','1657987915','1915258194',\
                '1628009324','2462605080','2478163131','1875034341']
    task=dict()
    task['task_name'] = '金融谣言识别'
    task['social_sensors'] = json.dumps(sensors)
    #create_sensing_task(task)
    es.delete(index=index_sensing,doc_type=type_sensing,id='AV9iqqb-p6BoxbAYrY0H')
    #es.delete(index=index_sensing,doc_type=type_sensing,id='AV9ip2eQp6BoxbAYrY0F')
    #es.delete(index=index_sensing,doc_type=type_sensing,id='AV9ipjv8p6BoxbAYrY0E')
