import get_redis
from pyjson import Json

local_json = Json('../cfg/local_db_cfg.json')
local_json.read_json_file()
local_redis = local_json.get_redis()
source_json = Json('../cfg/source_db_cfg.json')
source_json.read_json_file()
source_redis = source_json.get_redis()

local_client = get_redis.Get_redis(
        local_redis['host'],
        local_redis['port'],
        local_redis['db'],
        local_redis['password']
        )
local_client.create_connection()

source_client = get_redis.Get_redis(
        source_redis['host'],
        source_redis['port'],
        source_redis['db'],
        source_redis['password']
        )
source_client.create_connection()

local_client.delete_db()
source_client.back_up(local_client)
