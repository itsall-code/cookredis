import msgpack
import re


class Process:
    def __init__(self, data, platform, group, preLogin):
        self.original_data = data
        self.platform = platform
        self.group = group
        self.keys = [key.decode('utf-8') for key in data.keys()]
        self.values = [msgpack.unpackb(value) for value in data.values()]
        self.server_name = f"S{group}."
        self.preLogin = preLogin

    def get_keys(self):
        return self.keys

    def get_values(self):
        return self.values

    def get_local_keys(self):
        local_keys = [self.preLogin + key if not key.startswith(self.preLogin) else key for key in self.keys]
        return local_keys

    def get_local_values(self):
        local_values = [
            [
                [self.platform, self.group] + [re.sub(r'S\d+\.', self.server_name, item[2])] + item[3:]
                for item in sublist
            ] for sublist in self.values
        ]
        return [msgpack.packb(value) for value in local_values]

    def get_hash_data(self):
        local_keys = self.get_local_keys()
        local_values = self.get_local_values()
        return dict(zip(local_keys, local_values))

if __name__ == '__main__':
    data = {b'user1': msgpack.packb([[1, 2, 'S3.item1', 'value1']])}
    process = Process(data, 'platform1', 'group1', 'local_')
    hash_data = process.get_hash_data()
    print(hash_data)

