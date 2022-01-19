# # -*- coding: utf-8 -*-
# # @Time       : 2022/12/10
# # @Author     : xuefei
# # @File       : tasks.py
# # @Description: container异常监控告警
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
#         if not email_recipient:
#             email_recipient = 'liujiangfeng@chinamobile.com,shenyunyan@chinamobile.com'
#         if not phone_recipient:
#             phone_recipient = '13810673654,18717393754'
#         logging.info("获取到邮箱/手机号，email_recipient={},phone_recipient={}".format(email_recipient, phone_recipient))
#         return email_recipient, phone_recipient
#
#
# @task
# def alert_task(**kwargs):
#     """
#     告警任务
#     """
#     container = kwargs['container']
#     namespace = kwargs['namespace']
#     url = kwargs['url']
#     redis_key = kwargs['redis_key']
#     platform_name = kwargs['platform_name']
#     pod = kwargs['pod']
#     start_time = kwargs['start_time']
#
#     # 查询当前3分钟异常container
#     abnormal_data = get_container_abnormal_data(url)
#     # 判断当前container是否在异常数据内
#     if container in [item['metric']['container'] for item in abnormal_data]:
#         print('{}容器{}状态为waiting，发送告警'.format(platform_name, container))
#         """
#         获取namespace对应的用户邮件、手机号信息
#         调用邮件、短信告警接口进行告警
#         """
#         email_recipient, phone_recipient = get_alert_recipient(namespace)
#
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
#             'phone_message': 'Project_name: {}    Environment: 生产环境\r\n '
#                              'Service_instance_name: {}\r\n '
#                              'Start_alert_time: {}\r\n '
#                              'Alert_description: {}容器{}在生产环境中为非running状态，已经持续了{}分钟了'.format(
#                 namespace, pod, start_time, platform_name, container, continue_time
#             ),
#             'email_message': '<p>Project_name: {}     Environment: 生产环境</p>'
#                              '<p>Service_instance_name: {}</p> '
#                              '<p>Start_alert_time: {}</p> '
#                              '<p>Alert_description: {}容器{}在生产环境中为非running状态，已经持续了{}分钟了</p>'.format(
#                 namespace, pod, start_time, platform_name, container, continue_time
#             )
#         }
#         headers = {
#             'Accept-Charset': 'utf-8',
#             'Content-Type': 'application/json'
#         }
#         response = requests.post(url=settings.ALERT_SMS_URL, data=json.dumps(data), headers=headers)
#         if response.status_code == 200:
#             logging.info("{}容器{}报警信息发送成功！！！".format(platform_name, container))
#         else:
#             print(response)
#     else:
#         # 告警恢复，将定时任务删除
#         PeriodicTask.objects.get(name='AlertTask_{}'.format(container)).delete()
#         # 移除redis中当前container
#         conn = redis.Redis(connection_pool=POOL)
#         conn.srem(redis_key, container)
#
#
# def create_alert_task(**kwargs):
#     """
#     创建celery定时任务进行告警
#     """
#     container = kwargs['container']
#     namespace = kwargs['namespace']
#     url = kwargs['url']
#     redis_key = kwargs['redis_key']
#     platform_name = kwargs['platform_name']
#     pod = kwargs['pod']
#
#     # 创建定时任务查询告警状态，发送告警，每30分钟执行一次
#     schedule, _ = CrontabSchedule.objects.get_or_create(minute='*/30', hour='*', day_of_week='*', day_of_month='*',
#                                                         month_of_year='*', timezone='Asia/Shanghai')
#     periodic_task = PeriodicTask.objects.filter(name='AlertTask_{}'.format(container)).first()
#     if not periodic_task:
#         PeriodicTask.objects.create(
#             crontab=schedule,
#             name='AlertTask_{}'.format(container),
#             task='alert.tasks.alert_task',
#             start_time=datetime.datetime.now(),
#             kwargs=json.dumps({'container': container, 'namespace': namespace, 'url': url, 'redis_key': redis_key,
#                                'platform_name': platform_name, 'pod': pod, 'start_time': str(datetime.datetime.now())})
#         )
#
#
# @task
# def alert_task_once(**kwargs):
#     """
#     监测到首次异常异步执行告警任务1次
#     """
#     container = kwargs['container']
#     namespace = kwargs['namespace']
#     platform_name = kwargs['platform_name']
#     pod = kwargs['pod']
#
#     print('{}容器{}状态为非running，发送首次告警'.format(platform_name, container))
#     """
#     获取namespace对应的用户邮件、手机号信息
#     调用邮件、短信告警接口进行首次告警
#     """
#     email_recipient, phone_recipient = get_alert_recipient(namespace)
#     start_time = str(datetime.datetime.now())
#     if namespace:
#         if namespace.endswith('-dev'):
#             namespace = namespace[:-4]
#         else:
#             namespace = namespace[:-8]
#     data = {
#         'seq': str(uuid.uuid4()),
#         'email_recipient': email_recipient,
#         'phone_recipient': phone_recipient,
#         'phone_message': 'Project_name: {}   Environment: 生产环境\n'
#                          'Service_instance_name: {}\n'
#                          'Start_alert_time: {}\n'
#                          'Alert_description: {}容器{}生产环境中状态为非running'.format(
#             namespace, pod, start_time, platform_name, container
#         ),
#         'email_message': '<p>Project_name: {}    Environment: 生产环境</p>'
#                          '<p>Service_instance_name: {}</p>'
#                          '<p>Start_alert_time: {}</p>'
#                          '<p>Alert_description: {}容器{}生产环境中状态为非running</p>'.format(
#             namespace, pod, start_time, platform_name, container
#         )
#     }
#     headers = {
#         'Accept-Charset': 'utf-8',
#         'Content-Type': 'application/json'
#     }
#     response = requests.post(url=settings.ALERT_SMS_URL, data=json.dumps(data), headers=headers)
#     if response.status_code == 200:
#         logging.info("{}容器{}首次告警信息发送成功！！！".format(platform_name, container))
#     else:
#         print(response)
#
#
# def get_container_abnormal_data(url):
#     """
#     当前3分钟之内container异常
#     """
#     base_url = "{}/api/v1/query_range?".format(url)
#     start_time_array = time.strptime(
#         (datetime.datetime.now() - datetime.timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
#     ent_time_array = time.strptime(
#         (datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
#     start_time_stamp = time.mktime(start_time_array)
#     end_time_stamp = time.mktime(ent_time_array)
#     # 异常container信息
#     query_info = """sum(kube_pod_container_status_running{namespace=~".*"}!=1)by(pod,container,namespace)"""
#     query_url = "{}query={}&start={}&end={}&step=60s". \
#         format(base_url, query_info, start_time_stamp, end_time_stamp)
#     # 查询三分钟内异常 container信息
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
#         logging.info("无异常container")
#         return []
#
#
# @task
# def ai_ability_container_abnormal_develop():
#     """
#     ai能力平台研发集群异常
#     """
#     abnormal_data = get_container_abnormal_data(prometheus_develop_url)
#     # 将异常container写入redis
#     conn = redis.Redis(connection_pool=POOL)
#     for item in abnormal_data:
#         # 判断redis中是否有当前异常container，没有创建告警任务进行告警
#         if not conn.sismember('develop_abnormal_container', item["metric"]["container"]):
#             alert_task_once.delay(container=item["metric"]["container"], namespace=item["metric"]["namespace"],
#                                   platform_name='ai能力平台研发集群', pod=item["metric"]["pod"])
#             create_alert_task(container=item["metric"]["container"], namespace=item["metric"]["namespace"],
#                               url=prometheus_develop_url, redis_key='develop_abnormal_container',
#                               platform_name='ai能力平台研发集群', pod=item["metric"]["pod"])
#         conn.sadd('develop_abnormal_container', item["metric"]["container"])  # redis集合去重
#
#
# @task
# def ai_ability_container_abnormal_product():
#     """
#     ai能力平台生产集群异常
#     """
#     abnormal_data = get_container_abnormal_data(prometheus_product_url)
#     # 将异常container写入redis
#     conn = redis.Redis(connection_pool=POOL)
#     for item in abnormal_data:
#         # 判断redis中是否有当前异常container，没有创建告警任务进行告警
#         if not conn.sismember('product_abnormal_container', item["metric"]["container"]):
#             alert_task_once.delay(container=item["metric"]["container"], namespace=item["metric"]["namespace"],
#                                   platform_name='ai能力平台生产集群', pod=item["metric"]["pod"])
#             create_alert_task(container=item["metric"]["container"], namespace=item["metric"]["namespace"],
#                               url=prometheus_product_url, redis_key='product_abnormal_container',
#                               platform_name='ai能力平台生产集群', pod=item["metric"]["pod"])
#         conn.sadd('product_abnormal_container', item["metric"]["container"])  # redis集合去重
