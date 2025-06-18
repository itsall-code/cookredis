# 导包
# 连接Redis, 并创建连接池
import redis
from redis import ConnectionPool
# 解析values
import msgpack

# 获取Redis的连接类
# 接受参数 host，port，db，password
class Get_redis:
    # 类初始化
    def __init__(self, host, port, db, password):
        # 使用连接池连接Redis
        self.connection_pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password
        )
        self.client = redis.Redis(connection_pool=self.connection_pool)

    # 测试是否ping通
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
    
    # 获取key的Hash值
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
    
    # 获取db的全部的key
    def get_all_key(self):
        self.all_keys = self.client.keys()

    # 输出获取的Hash，测试数据是否正确
    # 最多输出5条
    def out_data(self, max_items=5):
        for index, (key, value) in enumerate(self.data.items()):
            if index >= max_items:
                break
            unpacked_key = key.decode()
            unpacked_value = msgpack.unpackb(value)
            print(f"{unpacked_key}: {unpacked_value}")
    
    # 更新Account Key 的values
    # 接收处理好的数据
    # 数据处理由process.py处理
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
    
    # 创建管道，加速备份效率
    def pipeline(self):
        return self.client.pipeline(transaction=False)

    # 备份
    # 接受需要到导入的Redis连接，与管道的最大处理数量
    def back_up(self, local_client, batch_size=1000):
        # 清库
        local_client.delete_db()
        
        keys = self.client.keys('*')
        total_keys = len(keys)
        print(f"开始备份，共 {total_keys} 个键")
        for i in range(0, total_keys, batch_size):
            batch_keys = keys[i:i+batch_size]
            pipeline = self.pipeline()
            local_pipeline = local_client.pipeline()
            for key in batch_keys:
                pipeline.dump(key)
            dumped_values = pipeline.execute()
            for key, value in zip(batch_keys, dumped_values):
                if value is not None:
                    local_pipeline.restore(key, 0, value, replace=True)
            local_pipeline.execute()
            print(f"进度: {min(i + batch_size, total_keys)}/{total_keys} 键已处理")
        print("备份完成")

    # 删除key
    def deleta_key(self, key):
        self.client.delete(key)

    # 删除db
    def delete_db(self):
        self.client.flushdb()

if __name__ == '__main__':
    redis_client = Get_redis("localhost", 6379, None, 1)
    redis_client.create_connection()
    data = redis_client.get_data("user")
    redis_client.out_data(data)

