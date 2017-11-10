# -*-coding:utf-8-*-

import sys
import math
import pickle
from elasticsearch import Elasticsearch
from feature_user_profile import user_fansnum
import json

reload(sys)
sys.path.append("../../")
from global_utils import es_flow_text, es_prediction, r_micro
from global_config import minimal_time_interval, pre_flow_text, type_flow_text, data_order, K,\
                            index_manage_prediction_task, type_manage_prediction_task, index_type_prediction_task
from time_utils import ts2datetime, datetime2ts, ts2date

# featrues are stored in task es with index_name of task_name 
# event is used to search weibo from es_prediction with event index_name
# update time is current ts, start_ts = current_ts - 3600


def organize_feature(task_name, event, start_ts, end_ts, during=3600):
    data = []
    index_list = []
    task_name = "micro_prediction_" + task_name


    while 1:
        data_dict = dict()
        if start_ts >= end_ts:
            break
        results_list = user_fansnum(event, start_ts, start_ts+during)
        for i in range(len(data_order)):
            data_dict[data_order[i]] = results_list[i]
        data_dict["update_time"] = start_ts+minimal_time_interval
        start_ts += during
        print "start timestamp: ",start_ts
        es_prediction.index(index=task_name, doc_type=index_type_prediction_task, id=start_ts, body=data_dict)

    #data_list = [total_fans_list,total_origin_list,total_retweet_list,total_comment_list,positive_count_list,neutral_count_list,negetive_count_list,origin_important_user_count,origin_important_user_retweet,retweet_important_user_count,retweet_important_user_retweet, total_count,average_origin_imp_hour_list,average_retweet_imp_hour_list]
    #y_value = total_count



# search the lastest 12 time interval data
# organise data feature

def prediction_task(task_name,current_ts, during=3600):
    # how many prediction work has done
    exist_count = 0
    task_detail = es_prediction.get(index=index_manage_prediction_task,doc_type=type_manage_prediction_task,id=task_name)["_source"]
    start_time = int(task_detail["start_time"])
    origin_task_name = task_name
    task_name = "micro_prediction_" + task_name

    while 1:
        start_time += during
        try:
            exist_work = es_prediction.get(index=task_name, doc_type="micro_task", id=start_time)["_source"]
            if exist_work["prediction_value"]:
                pass
        except:
            if exist_work:
                update_time = start_time
            else:
                update_time = start_time -during
            break
        exist_count += 1
    """
    if exist_count == 0:
        update_time = start_time
    else:
        update_time = start_time -during
    """

    if update_time > current_ts:
        return True
 
    else:
        while 1:
            if update_time > current_ts:
                print "update time: ",update_time
                print "current ts: ",current_ts
                break
            else:
                print "update time: ",update_time
                dispose_data(origin_task_name,update_time,during)
            update_time += during
         


def dispose_data(task_name,current_ts, during=3600):
    K = 2 ########

    task_detail = es_prediction.get(index=index_manage_prediction_task,doc_type=type_manage_prediction_task,id=task_name)["_source"]
    start_time = int(task_detail["start_time"])

    origin_task_name = task_name
    task_name = "micro_prediction_" + task_name




    query_body = {
        "query": {
            "range":{
                "update_time":{
                    "lte": current_ts
                }
            }
        },
        "size": K,
        "sort":{"update_time":{"order":"desc"}}
    }

    sort_query_body = {
        "query": {
            "range":{
                "update_time":{
                    "lte": current_ts
                }
            }
        }
    }

    total_count = []
    total_fans_list = []
    total_origin_list = []
    total_retweet_list = []
    total_comment_list = []
    total_uid_list = []
    total_positive_list = []
    total_negetive_list = []
    average_origin_ts = []
    average_retweet_ts = []

    feature_list = []
    results = es_prediction.search(index=task_name, doc_type=index_type_prediction_task, body=query_body)["hits"]["hits"]
    location = es_prediction.count(index=task_name, doc_type=index_type_prediction_task, body=sort_query_body)["count"]

    if len(results) != K:
        short_len = K - len(results)
        results.extend([[]]*short_len)
    print "former result: ", len(results), K
    results.reverse()
    for item in results:
        if item:
            item = item["_source"]
            #total_fans_list.append(item["total_fans_number"])
            total_origin_list.append(item["origin_weibo_number"])
            total_retweet_list.append(item["retweeted_weibo_number"])
            total_comment_list.append(item["comment_weibo_number"])
            total_count.append(item["total_count"])
            total_uid_list.append(item["total_uid_count"])
            total_positive_list.append(item["positive_count"])
            total_negetive_list.append(item["negetive_count"])
            average_origin_ts.append(item["average_origin_ts"])
            average_retweet_ts.append(item["average_retweet_ts"])
        else:
            #total_fans_list.append(0)
            total_origin_list.append(0)
            total_retweet_list.append(0)
            total_comment_list.append(0)
            total_uid_list.append(0)
            total_count.append(0)
            total_positive_list.append(0)
            total_negetive_list.append(0)
            average_origin_ts.append(0)
            average_retweet_ts.append(0)
    print "total_count: ", total_count

    feature_list = []
    feature_list.append(math.log(int(total_retweet_list[-1]+1)))
    feature_list.append(math.log(int(total_comment_list[-1]+1)))
    feature_list.append(math.log(int(total_positive_list[-1]+1)))
    feature_list.append(math.log(int(total_negetive_list[-2]+1)))
    feature_list.append(math.log(int(total_negetive_list[-1]+1)))
    feature_list.append(math.log(int(total_count[-1]+1)))
    feature_list.append(math.log(int(total_uid_list[-1]+1)))
    if int(during) == 3*3600:
        feature_list.append(average_origin_ts[-1])
        feature_list.append(average_retweet_ts[-1])


    # load model and prediction
    if int(during) == 3600:
        if total_count[-1] - total_count[-2] >= -0.2*total_count[-2]:
            with open("model-up.pkl","r") as f:
                gbdt = pickle.load(f)
        else:
            with open("model-down.pkl", "r") as f:
                gbdt = pickle.load(f)
    elif int(during) == 3*3600:
        with open("model-3.pkl","r") as f:
            gbdt = pickle.load(f)

    print "feature_list: ", feature_list
    pred = gbdt.predict(feature_list)
    for item in pred:
        prediction_value = item
        prediction_value = math.exp(prediction_value)
        print "prediction_valie: ",prediction_value


    # update scan processing
    #es_prediction.update(index=index_manage_prediction_task,doc_type=type_manage_prediction_task, \
    #        id=origin_task_name, body={"doc":{"scan_text_processing":"0"}})


    # update prediction value in es
    task_detail = es_prediction.get(index=index_manage_prediction_task, \
            doc_type=type_manage_prediction_task, id=origin_task_name)["_source"]
    if current_ts >= int(task_detail["stop_time"]):
        task_detail["finish"] = "1"
        task_detail["processing_status"] = "0"

        # update task info
        es_prediction.index(index=index_manage_prediction_task, \
            doc_type=type_manage_prediction_task, id=origin_task_name, body=task_detail)

    # update prediction
    es_prediction.update(index=task_name, doc_type=index_type_prediction_task, id=current_ts, body={"doc":{"prediction_value": prediction_value}})

    return True




if __name__ == "__main__":
    organize_feature("mao_ze_dong_dan_chen_ji_nian_ri","mao_ze_dong_dan_chen_ji_nian_ri" )



