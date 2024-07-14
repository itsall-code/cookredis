import process
import get_redis
from pyjson import Json
import os

# 初始化服务器参数，platform, group
# 初始化Redis参数，地址，端口号，密码，数据库编号，存放登陆账号的主键
def init_data(path):
    json = Json(path)
    json.read_json_file()
    json.get_redis()
    # print(local_json.read_json_file())
    return json


# 获取Redis 连接
def get_client(json):
    redis_data = json.get_redis()
    client = get_redis.Get_redis(
            redis_data['host'],
            redis_data['port'],
            redis_data['db'],
            redis_data['password']
    )
    client.create_connection()
    return client


# 初始化数据处理器
def init_process(client, json):
    client.get_data(json.json_data['account'])
    server_data = json.get_server()
    preLogin = json.json_data['preLogin']
    process_data = process.Process(
            client.data,
            server_data['platform'],
            server_data['group'],
            preLogin
            )
    process_data.get_keys()
    process_data.get_values()
    return process_data


# 获取处理好的数据
def get_local_data(process_data):
    process_data.get_local_keys()
    process_data.get_local_values()
    return process_data.get_hash_data()


# 涉及数据删除确认
def examine():
    examine_value = input('是否继续\n1.是\t2.否\n请选择:')
    match examine_value:
        case '1':
            return 1
        case _:
            return 0

if __name__ == '__main__':
    local_json = init_data('../cfg/local_db_cfg.json')
    door = 1
    while(door == 1):
        os.system('clear')
        print("请检查下面的配置与你的服务器配置是否一致")
        print("若不一致，可修改cfg目录下的local_db_cfg.json文件\n")
        local_json.out_data()
        choose = input(f"\n1. 确定一致，导入其他库到本服库\n2. 确定一致，本地化账户数据\n3. 确定一致，删除 db{local_json.redis_data['db']} \n4. 已修改，重新初始化\n0. 退出\n请选择: ")
        match choose:
            case '1':
                source_json = init_data('../cfg/source_db_cfg.json')
                print("请检查下面的配置与源数据库的Redis配置是否一致\n")
                source_json.out_data()
                print("若不一致，可修改cfg目录下的source_db_cfg.json文件")
                print("注意: 该操作会删除本服库，并导入源数据库的数据\n源数据库不会被影响\n")
                if(examine() == 1):
                    source_client = get_client(source_json)
                    source_client.back_up(local_client, 1000)
                else:
                    print("本次无进行拉取数据操作")
                input('输入任意键回到菜单')
            case '2':
                local_client = get_client(local_json)
                examine()
                process_data = init_process(local_client, local_json)
                local_data = get_local_data(process_data)
                # 兼容永恒，清理db库
                local_client.deleta_key('db')
                local_client.update(local_data)
                print("数据已本地化成功，部分数据如下: ")
                local_client.out_data()
                input('输入任意键回到菜单')
            case '3':
                print(f"该操作会删除 db{local_json.redis_data['db']}")
                if(examine() == 1):
                    local_client = get_client(local_json)
                    local_client.delete_db()
                    print(f"删除 db{local_json.redis_data['db']} 成功")
                else:
                    print(f"本次未删除 db{local_json.redis_data['db']}")
                input('输入任意键回到菜单')
            case '4':
                print("数据重新初始化")
                local_json = init_data()
                local_data = local_json.json_data
                input('输入任意键回到菜单')
            case '0':
                door = 0
                print('系统关闭成功')
                exit()
            case _:
                print('请输入正确的数据')
                input('输入任意键回到菜单')

