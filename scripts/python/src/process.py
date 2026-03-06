import msgpack
import re


# 数据处理器类
# 接受参数 原数据、服务器平台、服务器组号、本地服登陆前缀
class Process:
    # 类初始化
    def __init__(self, data, platform, group, preLogin):
        self.original_data = data
        self.platform = platform
        self.group = group
        self.keys = [key.decode('utf-8') for key in data.keys()]
        self.values = [msgpack.unpackb(value) for value in data.values()]
        self.server_name = f"S{group}."
        self.preLogin = preLogin

    # 获取keys
    def get_keys(self):
        return self.keys

    # 获取values
    def get_values(self):
        return self.values

    # 把原数据的keys 本地化加上登陆前缀
    def get_local_keys(self):
        local_keys = [self.preLogin + key if not key.startswith(self.preLogin) else key for key in self.keys]
        return local_keys

    # 修改原数据的values, 修改服务器平台与组号、名称标识SX.
    def get_local_values(self):
        local_values = [
            [
                [self.platform, self.group] + [re.sub(r'S\d+\.', self.server_name, item[2])] + item[3:]
                for item in sublist
            ] for sublist in self.values
        ]
        return [msgpack.packb(value) for value in local_values]
    
    # 把修改好的数据打包为hash
    def get_hash_data(self):
        local_keys = self.get_local_keys()
        local_values = self.get_local_values()
        return dict(zip(local_keys, local_values))

if __name__ == '__main__':
    data = {b'user1': msgpack.packb([[1, 2, 'S3.item1', 'value1']])}
    process = Process(data, 'platform1', 'group1', 'local_')
    hash_data = process.get_hash_data()
    print(hash_data)

