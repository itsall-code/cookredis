import redis
import msgpack
from redis import ConnectionPool

class Get_redis:
    def __init__(self, host, port, db, password):
        self.connection_pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password
        )
        self.client = redis.Redis(connection_pool=self.connection_pool)

    def create_connection(self):
        try:
            if self.client.ping():
                print("连接成功，正在处理中")
                return self.client
        except redis.ConnectionError as e:
            print(f"连接错误: {e}")
            # 可以添加重试逻辑或进一步处理
            return None
        except Exception as e:
            print(f"未知错误: {e}")
            return None

    def get_data(self, primary_key):
        try:
            self.primary_key = primary_key
            self.data = self.client.hgetall(primary_key)
            if self.data:
                return self.data
            else:
                print("未找到数据")
                return {}
        except redis.RedisError as e:
            print(f"获取数据失败: {e}")
            return {}

    def out_data(self, max_items=5):
        for index, (key, value) in enumerate(self.data.items()):
            if index >= max_items:
                break
            unpacked_key = key.decode()
            unpacked_value = msgpack.unpackb(value)
            print(f"{unpacked_key}: {unpacked_value}")

    def update(self, new_data):
        try:
            self.client.delete(self.primary_key)
            self.client.hset(self.primary_key, mapping=new_data)
            print(f"数据获取成功: {len(self.data)} 项")
            print("数据更新成功")
            return self.get_data(self.primary_key)
        except redis.RedisError as e:
            print(f"更新失败: {e}")
            return {}

    def deleta_key(self, key):
        self.client.delete(key)

    def delete_db(self):
        self.client.flushdb()

if __name__ == '__main__':
    redis_client = GetRedis("localhost", 6379, None, 1)
    redis_client.create_connection()
    data = redis_client.get_data("user")
    redis_client.out_data(data)

