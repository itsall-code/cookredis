import json


# 读取json 配置类
# 接受配置文件的路径
class Json:
    def __init__(self, file_path):
        self.path = file_path

    # 读取Json文件
    def read_json_file(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            self.json_data = json.load(file)
        return self.json_data

    # 获取redis配置
    def get_redis(self):
        self.redis_data = self.json_data['redis']
        return self.redis_data

    # 获取cross_redis
    def get_cross_redis(self):
        self.local_cross_redis_data = self.json_data['local_cross']
        self.source_cross_redis_data = self.json_data['source_cross']
        return [self.local_cross_redis_data, self.source_cross_redis_data]

    # 获取serer配置
    def get_server(self):
        self.server_data = self.json_data['server']
        return self.server_data

    # 获得delete表单配置
    def get_tb(self):
        self.tb_data = self.json_data['tb_name']
        return self.tb_data

    # 打印Json文件内容
    def out_data(self):
        formatted_json = json.dumps(self.json_data, indent=4)
        print(formatted_json)


# 测试
if __name__ == '__main__':
    file_path = '../cfg/new_local_db_cfg.json'
    local_json = Json(file_path)
    json_data = local_json.read_json_file()
    redis_data = json_data['redis']
    print(f"{redis_data['host']}")
    print(f"{local_json.get_redis()}")
    print(f"{local_json.get_server()}")
    local_json.out_data()
