import redis

# 创建连接到数据库 1 的 Redis 客户端
source_redis = redis.Redis(host='localhost', port=6379, db=1)

# 创建连接到数据库 2 的 Redis 客户端
target_redis = redis.Redis(host='localhost', port=6379, db=2)

# 获取数据库 1 中所有的键
keys = source_redis.keys()

# 遍历所有键并复制到数据库 2
for key in keys:
    # 获取键类型
    key_type = source_redis.type(key).decode('utf-8')
    
    # 根据键类型使用适当的 Redis 命令来复制数据
    if key_type == 'string':
        value = source_redis.get(key)
        target_redis.set(key, value)
    elif key_type == 'hash':
        value = source_redis.hgetall(key)
        target_redis.hset(key, mapping=value)
    elif key_type == 'list':
        list_items = source_redis.lrange(key, 0, -1)
        target_redis.rpush(key, *list_items)
    elif key_type == 'set':
        set_items = source_redis.smembers(key)
        target_redis.sadd(key, *set_items)
    elif key_type == 'zset':
        zset_items = source_redis.zrange(key, 0, -1, withscores=True)
        target_redis.zadd(key, dict(zset_items))

print("数据库 1 的数据已成功复制到数据库 2.")

