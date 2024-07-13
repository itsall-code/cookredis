import get_redis
import process


# 创建 Redis 连接
client = get_redis.Get_redis('localhost', 6379, None, 1)
client.create_connection()
# 读取键名为 'user' 的所有数据
data = client.get_data('user')
# 初始化处理类
process_data = process.Process(data, 2, 4)
process_data.get_keys()
process_data.get_values()


def test_1(client):

    if client.data:
        print("数据已成功从Redis读取.")
    else:
        print("Redis中没有找到相关数据.")
        return 1

    # 打印读取到的数据
    for key, value in client.data.items():
        # 打印键和值的前50个字符以简化输出
        print(f'Key: {key.decode()}, Value: {value[:50]}...')


def test_2(process_data):
    process_data.add_key('test1'.encode())
    process_data.add_key('test2'.encode())
    process_data.add_key('test3'.encode())
    process_data.get_local_keys()
    process_data.out_data()


def test_3(process_data):
    print(f"{process_data.values}")
    print(f"{process_data.get_local_values()}")


def test_4(process_data):
    process_data.get_local_keys
    process_data.get_local_values
    print(f"{process_data.data}")
    print(f"{process_data.get_hash_data()}")


def test_5(process_data, client):
    process_data.get_local_keys()
    process_data.get_local_values()
    new_data = process_data.get_hash_data()
    client.update(new_data)
    client.out_data()


# test_1(client)
# test_2(process_data)
# test_3(process_data)
# test_4(process_data)
# test_5(process_data, client)
