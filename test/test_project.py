from src.get_redis import Get_redis

client = Get_redis(host="localhost", port=6379, db=1)
client.create_connection()

client.get_all_key()
print(client.all_keys)
