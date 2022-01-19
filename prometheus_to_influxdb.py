#!/usr/bin/python
"""
读取Prometheus接口监控数据，写入txt，导入influxdb
"""
import json
import requests
import subprocess


def queryAll(address, expr):
    url = address + '/api/v1/query?query=' + expr
    response = requests.post(url=url)
    if response.status_code == 200 or response.status_code == '200':
        data = json.loads(response.content)
        return data['data']['result'][0]['values']


def data_get(url, method):
    address = 'http://172.22.16.157:19190'
    expr_status = 'probe_success{instance="%s"}[1d]' % url
    expr_duration = 'probe_duration_seconds{instance="%s"}[1d]' % url
    expr_status_code = 'probe_http_status_code{instance="%s"}[1d]' % url
    expr_content_length = 'probe_http_content_length{instance="%s"}[1d]' % url

    status_all = queryAll(address, expr_status)
    duration_all = queryAll(address, expr_duration)
    status_code_all = queryAll(address, expr_status_code)
    content_length_all = queryAll(address, expr_content_length)
    result = []
    for i in range(len(status_all)):
        data = {
            "name": "uptimecheck_http_2",
            "time": str(status_all[i][0])[:-4],
            "available": '1',
            "bk_cloud_id": '0',
            "charset": "utf-8",
            "content_length": content_length_all[i][1],
            "error_code": '0',
            "media_type": 'null',
            "message": "200OK",
            "method": method,
            "node_id": "1",
            "response_code": status_code_all[i][1],
            "status": 0 if status_all[i][1] else 1,
            "steps": "1",
            "task_duration": int(float(duration_all[i][1]) * 1000),
            "task_id": "2",
            "task_type": 'http',
            "url": url
        }
        result.append(data)
    return result


def write_to_txt(data, file):
    with open(file, 'w') as f1:  # 创建一个需要写入的txt文件
        f1.write('# DDL\n')
        # f1.write('\nCREATE DATABASE uptimecheck_2')  #创建数据库，若数据库已有则不需这段代码
        f1.write('\n# DML')
        f1.write('\n# CONTEXT-DATABASE: uptimecheck_2')  # 上面四行都是模板所需声明
        for i in data:
            f1.write('\nuptimecheck_http_2')  # measure写入

            f1.write(',bk_cloud_id=' + i['bk_cloud_id'])  # tag写入
            f1.write(',charset=' + i['charset'])  # tag写入
            f1.write(',error_code=' + i['error_code'])  # tag写入
            f1.write(',media_type=' + i['media_type'])  # tag写入
            f1.write(',message=' + i['message'])  # tag写入
            f1.write(',method=' + i['method'])  # tag写入
            f1.write(',node_id=' + i['node_id'])  # tag写入
            f1.write(',response_code=' + i['response_code'])  # tag写入
            f1.write(',status=%d' % int(i['status']))  # tag写入  bool
            f1.write(',task_id=' + i['task_id'])  # tag写入
            f1.write(',task_type=' + i['task_type'])  # tag写入
            f1.write(',url=' + i['url'])  # tag写入

            f1.write(' available=%d' % int(i['available']))  # fields写入  bool
            f1.write(',content_length=' + i['content_length'])  # fields写入
            f1.write(',steps=' + i['steps'])  # fields写入
            f1.write(',task_duration=' + str(i['task_duration']))  # fields写入
            f1.write(' ' + str(i['time']) + '000000000')  # fields写入
        f1.write('\n')  # 最后一行数据后需要回车，否则最后一条无法导入
    f1.close()


def subprocess_():
    """
    subprocess模块执行linux命令,写入数据库
    :return:
    """
    """
    influx -host 172.22.16.11 -port 5260 -import -path=influxbak_get1.txt -precision=ns -database=uptimecheck_2
    influx -host 172.22.16.11 -port 5260 -import -path=influxbak_get2.txt -precision=ns -database=uptimecheck_2
    influx -host 172.22.16.11 -port 5260 -import -path=influxbak_get0.txt -precision=ns -database=uptimecheck_2
    influx -host 172.22.16.11 -port 5260 -import -path=influxbak_post1.txt -precision=ns -database=uptimecheck_2
    influx -host 172.22.16.11 -port 5260 -import -path=influxbak_post2.txt -precision=ns -database=uptimecheck_2
    influx -host 172.22.16.11 -port 5260 -import -path=influxbak_post0.txt -precision=ns -database=uptimecheck_2
    """
    subprocess.call(
        "influx -host 172.22.16.11 -port 5260 -import -path=/root/prometheus_data/prometheus_data/influxbak_get0.txt -precision=ns -database=uptimecheck_2")  # 执行ls命令
    subprocess.call(
        "influx -host 172.22.16.11 -port 5260 -import -path=/root/prometheus_data/prometheus_data/influxbak_get1.txt -precision=ns -database=uptimecheck_2")  # 执行ls命令
    subprocess.call(
        "influx -host 172.22.16.11 -port 5260 -import -path=/root/prometheus_data/prometheus_data/influxbak_get2.txt -precision=ns -database=uptimecheck_2")  # 执行ls命令
    subprocess.call(
        "influx -host 172.22.16.11 -port 5260 -import -path=/root/prometheus_data/prometheus_data/influxbak_post0.txt -precision=ns -database=uptimecheck_2")  # 执行ls命令
    subprocess.call(
        "influx -host 172.22.16.11 -port 5260 -import -path=/root/prometheus_data/prometheus_data/influxbak_post1.txt -precision=ns -database=uptimecheck_2")  # 执行ls命令
    subprocess.call(
        "influx -host 172.22.16.11 -port 5260 -import -path=/root/prometheus_data/prometheus_data/influxbak_post2.txt -precision=ns -database=uptimecheck_2")  # 执行ls命令


if __name__ == '__main__':
    all_url_get = [
        "http://172.22.16.228:30080/verification4aiip/product/ttsgpubmgt/TTS_Service",
        "http://172.22.16.228:30080/verification4aiip/product/textclzc3h4/service",
        "http://172.22.16.228:30080/verification4aiip/product/namedentityyjyf0yy/bertner"
    ]
    all_url_post = [
        "http://172.22.16.228:30080/verification4aiip/product/docvbgp/nlp-service/extract",
        "http://172.22.16.228:30080/verification4aiip/product/idcardocracqv/idcardocr",
        "http://172.22.16.228:30080/verification4aiip/product/mcloudimageclassify3n2c/cmic/mcloud/v1.5/image/label/"
    ]
    a = 0
    for url in all_url_get:
        print(url + '任务开始')
        result = data_get(url, 'GET')
        write_to_txt(result, './prometheus_data/influxbak_get%d.txt' % a)
        a += 1
        print(url + '任务结束')

    b = 0
    for url in all_url_post:
        print(url + '任务开始')
        result = data_get(url, 'POST')
        write_to_txt(result, './prometheus_data/influxbak_post%d.txt' % b)
        b += 1
        print(url + '任务结束')

    # subprocess_()
