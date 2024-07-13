import msgpack

class Process:
    # 初始化类
    def __init__(self, data, number):
        self.data = data
        self.number = number

    # 获取key
    def get_keys(self):
        self.keys = list(self.data.keys())  # 更新self.keys
        return self.keys

    # 获取value
    def get_values(self):
        self.values = list(self.data.values())
        return self.values

    # keys local
    # 在每个账号前加上 'local_' 方便内网登陆
    def get_local_keys(self):
        keys = [key.decode('utf-8') for key in self.keys]
        local_keys = [
            key if key.startswith('local') else 'local_' + key
            for key in keys
        ]
        self.local_keys = [key.encode() for key in local_keys]
        return self.local_keys

    # values local
    # 修改服务器编号，与内网数据对应
    def get_local_values(self):
        server_name = f"S{self.number}"
        values = [msgpack.unpackb(value) for value in self.values]
        local_values = [
            [
                [item[0], self.number] + [item[2].replace('S3', server_name)] + item[3:] for item in sublist
            ]
            for sublist in values
        ]
        self.local_values = [msgpack.packb(value) for value in local_values]
        return self.local_values


    # 把keys 和 values 处理为hash
    def get_hash_data(self):
        self.hash_data = {key : value for key, value in zip(self.local_keys, self.local_values)}
        return self.hash_data

    # 打印数据,调试使用
    def out_data(self):
        print(f"{self.data}")
        print(f"{self.keys}")
        print(f"{self.values}")

    def out_local_data(self):
        print(f"{self.local_keys}")
        print(f"{self.local_values}")

    # 添加key到data,测试使用
    def add_key(self, key):
        return self.keys.append(key)
