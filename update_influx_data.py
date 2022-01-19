"""
influxdb数据导出csv文件，修改数据转换成txt，导入influxdb
"""
import csv

with open('./data/update.txt', 'w') as f1:  # 创建一个需要写入的txt文件
    f1.write('# DDL\n')
    # f1.write('\nCREATE DATABASE uptimecheck_2')  #创建数据库，若数据库已有则不需这段代码
    f1.write('\n# DML')
    f1.write('\n# CONTEXT-DATABASE: uptimecheck_2')  # 上面四行都是模板所需声明

    with open('./data/data/update.csv') as csvfile:
        readcsv = csv.reader(csvfile)

        for row in list(readcsv)[1:]:
            f1.write('\nuptimecheck_http_2')  # measure写入

            f1.write(',bk_cloud_id=' + row[3])  # tag写入
            f1.write(',charset=' + row[4])  # tag写入
            f1.write(',error_code=' + str(0))  # tag写入
            f1.write(',media_type=' + row[7])  # tag写入
            f1.write(',message=' + '200OK')  # tag写入
            f1.write(',method=' + row[9])  # tag写入
            # f1.write(',method=' + 'GET')  # tag写入
            f1.write(',node_id=' + row[10])  # tag写入
            f1.write(',response_code=' + '200')  # tag写入
            f1.write(',status=%d' % 0)  # tag写入
            f1.write(',task_id=' + row[15])  # tag写入
            f1.write(',task_type=' + row[16])  # tag写入
            f1.write(',url=' + row[17])  # tag写入

            f1.write(' available=%d' % 1)  # fields写入
            f1.write(',content_length=' + row[5])  # fields写入
            f1.write(',steps=' + row[13])  # fields写入
            f1.write(',task_duration=' + row[14])  # fields写入

            # f1.write(' ' + str(int(row[1]) - 5356800000000000))  # fields写入
            f1.write(' ' + str(int(row[1])))  # fields写入

    f1.write('\n')  # 最后一行数据后需要回车，否则最后一条无法导入
f1.close()

"""
influx --port 5260 --host 172.22.16.11  -database "uptimecheck_2"  -execute "select * from uptimecheck_http_2 where url='http://172.22.16.228:30080/verification4aiip/product/nginx1web1/' and response_code=503" -format csv  >>  update.csv
influx -host 172.22.16.11 -port 5260 -import -path=all_bu2.txt -precision=ns -database=uptimecheck_2
"""

# insert uptimecheck_http_2,url=http://172.22.16.228:30080/verification4aiip/product/keywordaeuq/nlp/get_keywords available=1,bk_cloud_id=0,charset=utf-8,content_length=79,error_code=0,media_type='',message=200 OK,method=POST,node_id=1,response_code=200,status=0,steps=1,task_duration=7,task_id=2,task_type=http 1635955202000000000
