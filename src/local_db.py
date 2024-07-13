import process
import get_redis
from pyjson import Json


# 初始化服务器参数，platform, group
# 初始化redis参数，地址，端口号，密码，数据库编号，存放登陆账号的主键
def init_data():

    local_path = '../cfg/local_db_cfg.json'
    local_json = Json(local_path)
    local_json.read_json_file()
    # print(local_json.read_json_file())
    return local_json


def get_client(local_data):
    client = get_redis.Get_redis(
            local_data['host'],
            local_data['port'],
            local_data['pwd'],
            local_data['db']
    )
    client.create_connection()
    client.get_data(local_data['primary_key'])
    return client


def init_process(client, local_data):
    process_data = process.Process(
            client.data,
            local_data['platform'],
            local_data['group']
            )
    process_data.get_keys()
    process_data.get_values()
    return process_data


def get_local_data(process_data):
    process_data.get_local_keys()
    process_data.get_local_values()
    return process_data.get_hash_data()

if __name__ == '__main__':

    local_json = init_data()
    local_data = local_json.json_data
    
    door = 1

    while(door == 1):
        print("请检查下面的配置与你的服务器配置是否一致")
        print("若不一致，可修改cfg目录下的local_db_cfg.json文件\n")
        local_json.out_data()
        choose = input("\n1. 与配置一致，可本地化数据\t2. 已修改，重新初始化\t3. 退出\n请选择: ")
        
        match choose:
            case '1':
                client = get_client(local_data)
                process_data = init_process(client, local_data)
                local_data = get_local_data(process_data)
                client.update(local_data)
                print("数据已本地化成功，部分数据如下: ")
                client.out_data()
                input('输入任意键回到菜单')
            case '2':
                print("数据重新初始化")
                local_json = init_data()
                local_data = local_json.json_data
            case '3':
                door = 0
                print('系统关闭成功')
                exit()
            case _:
                print('输入正确的数据')

