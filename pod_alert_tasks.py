# # -*- coding: utf-8 -*-
# # @Time       : 2022/12/10
# # @Author     : xuefei
# # @File       : pod_alert_tasks.py
# # @Description: pod异常监控告警
#
# import json
# import datetime
# import logging
# import time
# import uuid
#
# import redis
# import requests
# from celery import task
# from django_celery_beat.models import PeriodicTask, CrontabSchedule
# from django.conf import settings
#
# from dataget.prometheus_data import prometheus_develop_url, prometheus_product_url
#
# POOL = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB,
#                             max_connections=100)
#
#
# def get_alert_recipient(namespace):
#     """
#     根据namespace获取告警接收人
#     """
#     request_url = settings.ALERT_RECIPIENT_URL.format(namespace)
#     response_tmp = requests.get(request_url)
#     if response_tmp.status_code != 200:
#         logging.info("访问：{}，状态不为 200".format(request_url))
#         return None, None
#     response_json = json.loads(response_tmp.content)
#
#     if response_json["state"] != "OK":
#         logging.info("访问：{}，state 不为 OK".format(request_url))
#         return None, None
#
#     if "body" in response_json:
#         email_recipient = response_json['body']['alarmEmail']
#         phone_recipient = response_json['body']['alarmTelephone']
#         logging.info("获取到邮箱/手机号，email_recipient={},phone_recipient={}".format(email_recipient, phone_recipient))
#         return email_recipient, phone_recipient
#
#
# @task
# def alert_task(**kwargs):
#     """
#     告警任务
#     """
#     namespace = kwargs['namespace']
#     url = kwargs['url']
#     redis_key = kwargs['redis_key']
#     platform_name = kwargs['platform_name']
#     pod = kwargs['pod']
#     phase = kwargs['phase']
#     start_time = kwargs['start_time']
#
#     # 查询当前3分钟异常container
#     abnormal_data = get_pod_abnormal_data(url)
#     # 判断当前container是否在异常数据内
#     if pod in [item['metric']['pod'] for item in abnormal_data]:
#         print('{}pod:{}状态为{}，发送告警'.format(platform_name, pod, phase))
#         """
#         获取namespace对应的用户邮件、手机号信息
#         调用邮件、短信告警接口进行告警
#         """
#         email_recipient, phone_recipient = get_alert_recipient(namespace)
#         start_t = time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f"))
#         now_time = time.mktime(datetime.datetime.now().timetuple())
#         continue_time = (now_time - start_t) // 60
#
#         if namespace:
#             if namespace.endswith('-dev'):
#                 namespace = namespace[:-4]
#             else:
#                 namespace = namespace[:-8]
#         data = {
#             'seq': str(uuid.uuid4()),
#             'email_recipient': email_recipient,
#             'phone_recipient': phone_recipient,
#             'message': 'project_name: {}  environment: 生产环境\n'
#                        'service_instance_name: {}\n'
#                        'start_alerm_time: {}\n'
#                        'alerm_description: {}pod,{}生产环境中状态为{}，已经持续了{}分钟了'.format(
#                 namespace, pod, start_time, platform_name, pod, phase, continue_time
#             )
#         }
#         headers = {
#             'Accept-Charset': 'utf-8',
#             'Content-Type': 'application/json'
#         }
#         response = requests.post(url=settings.ALERT_SMS_URL, data=json.dumps(data), headers=headers)
#         if response.status_code == 200:
#             logging.info("{}pod,{}报警信息发送成功！！！".format(platform_name, pod))
#         else:
#             print(response)
#     else:
#         # 告警恢复，将定时任务删除
#         PeriodicTask.objects.get(name='AlertTask_{}'.format(pod)).delete()
#         # 移除redis中当前pod
#         conn = redis.Redis(connection_pool=POOL)
#         conn.srem(redis_key, pod)
#
#
# def create_alert_task(**kwargs):
#     """
#     创建celery定时任务进行告警
#     """
#     namespace = kwargs['namespace']
#     url = kwargs['url']
#     redis_key = kwargs['redis_key']
#     platform_name = kwargs['platform_name']
#     pod = kwargs['pod']
#     phase = kwargs['phase']
#
#     # 创建定时任务查询告警状态，发送告警，每20分钟执行一次
#     schedule, _ = CrontabSchedule.objects.get_or_create(minute='*/20', hour='*', day_of_week='*', day_of_month='*',
#                                                         month_of_year='*', timezone='Asia/Shanghai')
#     task = PeriodicTask.objects.filter(name='AlertTask_{}'.format(pod)).first()
#     if not task:
#         PeriodicTask.objects.create(
#             crontab=schedule,
#             name='AlertTask_{}'.format(pod),
#             task='alert.tasks.alert_task',
#             start_time=datetime.datetime.now(),
#             kwargs=json.dumps({'pod': pod, 'namespace': namespace, 'phase': phase, 'url': url, 'redis_key': redis_key,
#                                'platform_name': platform_name, 'start_time': str(datetime.datetime.now())})
#         )
#
#
# def get_pod_abnormal_data(url):
#     """
#     当前3分钟之内pod异常
#     """
#     base_url = "{}/api/v1/query_range?".format(url)
#     start_time_array = time.strptime(
#         (datetime.datetime.now() - datetime.timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
#     ent_time_array = time.strptime(
#         (datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
#     start_time_stamp = time.mktime(start_time_array)
#     end_time_stamp = time.mktime(ent_time_array)
#     # 异常pod信息
#     query_info = """sum(kube_pod_status_phase{namespace=~".*", phase=~"Failed|Unknown|Pending"}==1)by(namespace,pod,phase,instance)"""
#
#     query_url = "{}query={}&start={}&end={}&step=60s". \
#         format(base_url, query_info, start_time_stamp, end_time_stamp)
#     # 查询三分钟内异常 pod信息
#     response_tmp = requests.get(query_url)
#     if response_tmp.status_code != 200:
#         logging.info("访问：{}，状态不为 200".format(query_url))
#         return []
#     response_json = json.loads(response_tmp.content)
#     if "data" in response_json:
#         response_data = response_json['data']['result']
#         abnormal_data = []
#         # 过滤掉namespace名不是以-dev或-product结尾的
#         for item in response_data:
#             if item["metric"]["namespace"].endswith("-dev") or item["metric"]["namespace"].endswith("-product"):
#                 abnormal_data.append(item)
#         return abnormal_data
#     else:
#         logging.info("无异常pod")
#         return []
#
#
# @task
# def ai_ability_pod_abnormal_develop():
#     """
#     ai能力平台研发集群异常
#     """
#     abnormal_data = get_pod_abnormal_data(prometheus_develop_url)
#     # 将异常container写入redis
#     conn = redis.Redis(connection_pool=POOL)
#     for item in abnormal_data:
#         # 判断redis中是否有当前异常container，没有创建告警任务进行告警
#         if not conn.sismember('develop_abnormal_pod', item["metric"]["pod"]):
#             create_alert_task(namespace=item["metric"]["namespace"], pod=item["metric"]["pod"],
#                               phase=item["metric"]["phase"],
#                               url=prometheus_develop_url, redis_key='develop_abnormal_pod',
#                               platform_name='ai能力平台研发集群')
#         conn.sadd('develop_abnormal_pod', item["metric"]["pod"])  # redis集合去重
#
#
# @task
# def ai_ability_pod_abnormal_product():
#     """
#     ai能力平台生产集群异常
#     """
#     abnormal_data = get_pod_abnormal_data(prometheus_product_url)
#     # 将异常container写入redis
#     conn = redis.Redis(connection_pool=POOL)
#     for item in abnormal_data:
#         # 判断redis中是否有当前异常container，没有创建告警任务进行告警
#         if not conn.sismember('product_abnormal_pod', item["metric"]["pod"]):
#             create_alert_task(pod=item["metric"]["pod"], namespace=item["metric"]["namespace"],
#                               phase=item["metric"]["phase"],
#                               url=prometheus_product_url, redis_key='product_abnormal_pod',
#                               platform_name='ai能力平台生产集群')
#         conn.sadd('product_abnormal_pod', item["metric"]["pod"])  # redis集合去重
