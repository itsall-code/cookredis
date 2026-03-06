from get_redis import Get_redis

# 创建 Redis 连接
client = Get_redis('localhost', 6379, "", 0)
client.create_connection()

keys = client.get_all_key()
print(keys)
