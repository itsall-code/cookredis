import json


class Json:
    def __init__(self, file_path):
        self.path = file_path

    # 读取Json文件
    def read_json_file(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            self.json_data = json.load(file)
        return self.json_data

    # 打印Json文件内容
    def out_data(self):
        formatted_json = json.dumps(self.json_data, indent=4)
        print(formatted_json)


# 使用示例
if __name__ == '__main__':
    file_path = '../cfg/local_db_cfg.json'
    local_json = Json(file_path)
    json_data = local_json.read_json_file()
    print(f"{json_data['host']}")
    local_json.out_data()
