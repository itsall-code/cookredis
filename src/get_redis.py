import redis
import msgpack

class Get_redis:
    def __init__(self, host, port, pwd, db):
        self.host = host
        self.port = port
        self.password = pwd
        self.db = db

    def create_connection(self):
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db
            )
            if self.client.ping():
                print("连接成功")
                return self.client
        except Exception as e:
            print(f"连接失败: {e}")
            return None

    def get_data(self, primary_key):
        try:
            self.primary_key = primary_key
            self.data = self.client.hgetall(self.primary_key)
            return self.data
        except Exception as e:
            print(f"获取数据失败: {e}")
            return None

    def out_data(self):
        for item in self.data.items():
            unpacked_key = item[0].decode()
            unpacked_value = msgpack.unpackb(item[1])
            print(f"{unpacked_key}: {unpacked_value}\n")

    def update(self, new_data):
        self.client.delete(self.primary_key)
        self.client.hset(self.primary_key, mapping=new_data)
        return self.get_data(self.primary_key)

if __name__ == '__main__':
    redis_client = Get_redis("localhost", 6379,"" , 1)
    redis_client.create_connection()
    redis_client.get_data("user")
    redis_client.out_data()

