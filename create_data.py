"""
influxdb中接口监控数据创建，写入txt，导入influxdb
"""
import random
import time


def create_data(file, url, method, start_time, end_time):
    with open(file, 'w') as f1:  # 创建一个需要写入的txt文件
        f1.write('# DDL\n')
        # f1.write('\nCREATE DATABASE uptimecheck_2')  #创建数据库，若数据库已有则不需这段代码
        f1.write('\n# DML')
        f1.write('\n# CONTEXT-DATABASE: uptimecheck_2')  # 上面四行都是模板所需声明
        # for i in range(1, 2):
        #     s = str(i)

        time = start_time
        while time < end_time:
            f1.write('\nuptimecheck_http_2')  # measure写入

            f1.write(',bk_cloud_id=0')  # tag写入
            f1.write(',charset=utf-8')  # tag写入
            f1.write(',error_code=0')  # tag写入
            f1.write(',media_type=null')  # tag写入
            f1.write(',message=200OK')  # tag写入
            f1.write(',method=' + method)  # tag写入
            f1.write(',node_id=1')  # tag写入
            f1.write(',response_code=200')  # tag写入
            f1.write(',status=%d' % int(0))  # tag写入
            # f1.write(',task_id=' + str(random.randint(1, 20)))  # tag写入
            f1.write(',task_id=' + str(8))  # tag写入
            f1.write(',task_type=http')  # tag写入
            f1.write(',url=' + url)  # tag写入

            f1.write(' available=%d' % int(1))  # fields写入
            # f1.write(',content_length=' + str(random.randint(100, 150)))  # fields写入
            f1.write(',content_length=' + str(612))  # fields写入
            f1.write(',steps=1')  # fields写入
            f1.write(',task_duration=' + str(random.randint(50, 2000)))  # fields写入

            f1.write(' ' + str(int(time)) + '000000000')  # fields写入
            time += 60
        f1.write('\n')  # 最后一行数据后需要回车，否则最后一条无法导入
    f1.close()


if __name__ == '__main__':
    create_data(
        file='./data/f225.txt',
        url='http://172.22.16.225:30080/verification4aiip/product/nginx1web1/',
        method='GET',
        start_time=time.mktime(time.strptime('2021-11-15 00:00:00', "%Y-%m-%d %H:%M:%S")),
        end_time=time.mktime(time.strptime('2021-11-16 00:00:00', "%Y-%m-%d %H:%M:%S"))
    )
    """
    influx -host 172.22.16.11 -port 5260 -import -path=f225.txt -precision=ns -database=uptimecheck_2
    """
