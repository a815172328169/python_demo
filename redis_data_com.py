# -*- coding: utf-8 -*-
"""
@Author     : XueFei
@File       : redis_data_com.py
@Time       : 2022/1/13 16:59
@Description: 
"""
import datetime
import json

import redis

Pool = redis.ConnectionPool(host='127.0.0.1', port='6379', db=2, max_connections=100, decode_responses=True)
with open("./data/data.json", 'r', encoding='utf8') as f:
    response_json = json.loads(f.read())

conn = redis.Redis(connection_pool=Pool)
if 'data' in response_json:
    response_data = response_json['data']['result']
    abnormal_data = []
    if conn.hlen('container_status_1') == 0:
        for item in response_data:
            conn.hsetnx('container_status_1', item['metric']['container'], item['value'][1])
    elif conn.hlen('container_status_2') == 0:
        for item in response_data:
            conn.hsetnx('container_status_2', item['metric']['container'], item['value'][1])
    elif conn.hlen('container_status_3') == 0:
        for item in response_data:
            conn.hsetnx('container_status_3', item['metric']['container'], item['value'][1])
    else:
        for item in response_data:
            a = conn.hget('container_status_1', item['metric']['container'])

            if conn.hget('container_status_1', item['metric']['container']) == '1' and conn.hget('container_status_2',
                                                                                               item['metric'][
                                                                                                   'container']) == '1' and conn.hget(
                'container_status_3', item['metric']['container']) == '1' and item['value'][1] == '0':
                if item["metric"]["namespace"].endswith("-dev") or item["metric"]["namespace"].endswith("-product"):
                    abnormal_data.append(item)
            if conn.hget('container_status_1', item['metric']['container']) == '1' and conn.hget('container_status_2',
                                                                                               item['metric'][
                                                                                                   'container']) == '1' and conn.hget(
                'container_status_3', item['metric']['container']) == '0' and item['value'][1] == '0':
                if item["metric"]["namespace"].endswith("-dev") or item["metric"]["namespace"].endswith("-product"):
                    abnormal_data.append(item)
        print(abnormal_data)
        start_time = datetime.datetime.now()
        # ?????????1??????redis???????????????2???????????????1?????????key???
        conn.delete('container_status_1')
        data1 = conn.hgetall('container_status_2')
        conn.hmset('container_status_1', data1)
        # ?????????2??????redis???????????????3???????????????2?????????key???
        conn.delete('container_status_2')
        data2 = conn.hgetall('container_status_3')
        conn.hmset('container_status_2', data2)
        # ?????????3??????redis???????????????4???????????????3?????????key???
        conn.delete('container_status_3')
        for item in response_data:
            conn.hsetnx('container_status_3', item['metric']['container'], item['value'][1])
        end_time = datetime.datetime.now()
        print(end_time-start_time)




