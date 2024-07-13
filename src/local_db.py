import process
import get_redis
from pyjson import Json


# 初始化服务器参数，platform, group
# 初始化redis参数，地址，端口号，密码，数据库编号，存放登陆账号的主键
def init_data():

    local_path = '../cfg/new_local_db_cfg.json'
    local_json = Json(local_path)
    local_json.read_json_file()
    local_json.get_server()
    local_json.get_redis()
    # print(local_json.read_json_file())
    return local_json


def get_client(local_json):
    redis_data = local_json.get_redis()
    key = local_json.json_data['account']
    client = get_redis.Get_redis(
            redis_data['host'],
            redis_data['port'],
            redis_data['db'],
            redis_data['password']
    )
    client.create_connection()
    client.get_data(key)
    return client


def init_process(client, local_json):
    server_data = local_json.get_server()
    preLogin = local_json.json_data['preLogin']
    process_data = process.Process(
            client.data,
            server_data['platform'],
            server_data['group'],
            preLogin
            )
    process_data.get_keys()
    process_data.get_values()
    return process_data


def get_local_data(process_data):
    process_data.get_local_keys()
    process_data.get_local_values()
    return process_data.get_hash_data()

def examine():
    confirm = input("操作前请确认服务器是否关闭\n输入1确认关闭");
    match confirm:
        case '1':
            return 1
        case _:
            examine()
    
if __name__ == '__main__':
    
    local_json = init_data()
    client = get_client(local_json)

    door = 1

    while(door == 1):
        print("请检查下面的配置与你的服务器配置是否一致")
        print("若不一致，可修改cfg目录下的local_db_cfg.json文件\n")
        local_json.out_data()
        choose = input("\n1. 与配置一致，可本地化数据\t2. 已修改，重新初始化\t3. 退出\n4.清库\n请选择: ")
        
        match choose:
            case '1':
                examine()
                process_data = init_process(client, local_json)
                local_data = get_local_data(process_data)
                # 兼容永恒，清理db库
                client.deleta_key('db')
                client.update(local_data)
                print("数据已本地化成功，部分数据如下: ")
                client.out_data()
                input('输入任意键回到菜单')
            case '2':
                print("数据重新初始化")
                local_json = init_data()
                local_data = local_json.json_data
                client = get_client(local_json)
            case '3':
                door = 0
                print('系统关闭成功')
                exit()
            case '4':
                client.delete_db()
                print(f"清除{local_json.redis_data['db']}数据库成功")
            case _:
                print('输入正确的数据')

