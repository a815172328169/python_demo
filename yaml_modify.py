import yaml
"""
yaml文件读取，更改
"""

def modify_s(a ,b):
    if a == 'SMS_PHONE_1':
        yaml_name = 'config_cmcc_grafana.yaml'

    # 修改yaml配置
    with open(yaml_name, 'r', encoding='utf-8') as f:
        # print(f.read())
        result = f.read()
        config = yaml.load(result, Loader=yaml.FullLoader)
        print(config[a])
        # 修改的值
        config[a] = b
        with open(yaml_name, 'w', encoding='utf-8') as w_f:
            # 覆盖原先的配置文件
            yaml.dump(config, w_f)
modify_s('SMS_PHONE_1', '12331231;2312312')

