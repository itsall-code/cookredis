import process
import get_redis
from pyjson import Json
import os
from pipeline import Pipeline


# 初始化服务器参数，platform, group
# 初始化Redis参数，地址，端口号，密码，数据库编号，存放登陆账号的主键
def init_data(path):
    json = Json(path)
    json.read_json_file()
    json.get_redis()
    # print(local_json.read_json_file())
    return json


# 初始化批量处理流水线
def init_pipeline(path):
    pipeline = Pipeline(path)
    pipeline.get_cfg_folders()
    return pipeline


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

# 获取跨服Redis 连接
#

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


# 删除外网库与内网不一致的数据表单
def delete_tb(path, local_client):
    delete_tb_cfg = Json(path)
    delete_tb_cfg.read_json_file()
    tb_data = delete_tb_cfg.get_tb()
    for tb_name in iter(tb_data):
        local_client.deleta_key(tb_name)
        print(f"{tb_name}清理成功")


# 涉及数据删除确认
def examine():
    examine_value = input('是否继续\n1.是\t2.否\n请选择:')
    match examine_value:
        case '1':
            return 1
        case _:
            return 0


def clear():
    os.system('cls')


if __name__ == '__main__':
    local_json = init_data('../cfg/local_db_cfg.json')
    door = 1
    while (door == 1):
        clear()
        print("请检查下面的配置与你的服务器配置是否一致")
        print("若不一致，可修改cfg目录下的local_db_cfg.json文件\n")
        local_json.out_data()
        choose = input(f"\n1.确定一致，导入其他库到本服库\n2.确认一致，备份本服库到其他库\n3.确定一致，本地化账户数据\n4.确定一致，删除 db{local_json.redis_data['db']}\n5.已修改，重新初始化\n6.批量本地化操作\n0.退出\n请选择: ")
        match choose:
            case '1':
                clear()
                source_json = init_data('../cfg/source_db_cfg.json')
                print("请检查下面的配置与源数据库的Redis配置是否一致\n")
                source_json.out_data()
                print("\n若不一致，可修改cfg目录下的source_db_cfg.json文件")
                print("注意: 该操作会删除本服库，并导入源数据库的数据\n源数据库不会被影响")
                if (examine() == 1):
                    local_client = get_client(local_json)
                    source_client = get_client(source_json)
                    source_client.back_up(local_client, 1000)
                else:
                    print("本次无进行拉取数据操作")
                input('输入任意键回到菜单')
            case '2':
                clear()
                backup_json = init_data('../cfg/backup_db_cfg.json')
                print("请检查下面的配置与备份数据库的Redis配置是否一致\n")
                source_json.out_data()
                print("\n若不一致，可修改cfg目录下的backup_db_cfg.json文件")
                print("注意: 该操作会删除该备份库，并导入本服库的数据\n本服库不会被影响")
                if (examine() == 1):
                    local_client = get_client(local_json)
                    backup_client = get_client(backup_json)
                    local_client.back_up(backup_json, 1000)
                else:
                    print("本次无进行备份数据操作")
                input('输入任意键回到菜单')
            case '3':
                clear()
                local_client = get_client(local_json)
                examine()
                process_data = init_process(local_client, local_json)
                local_data = get_local_data(process_data)
                delete_tb('../cfg/del_tb.json', local_client)
                local_client.update(local_data)
                print("数据已本地化成功，部分数据如下: ")
                local_client.out_data()
                input('输入任意键回到菜单')
            case '4':
                clear()
                print(f"该操作会删除 db{local_json.redis_data['db']}")
                if (examine() == 1):
                    local_client = get_client(local_json)
                    local_client.delete_db()
                    print(f"删除 db{local_json.redis_data['db']} 成功")
                else:
                    print(f"本次未删除 db{local_json.redis_data['db']}")
                input('输入任意键回到菜单')
            case '5':
                clear()
                print("数据重新初始化")
                local_json = init_data('../cfg/local_db_cfg.json')
                local_data = local_json.json_data
                input('输入任意键回到菜单')
            case '6':
                clear()
                print("批量处理多个配置文件")
                pipeline = init_pipeline('../pipeline')
                for process_path in pipeline.folders:
                    local_path = process_path.joinpath('local_db_cfg.json')
                    source_path = process_path.joinpath('source_db_cfg.json')
                    localWorkJson = init_data(local_path)
                    sourceWorkJson = init_data(source_path)
                    localWorkClient = get_client(localWorkJson)
                    sourceWorkClient = get_client(sourceWorkJson)
                    sourceWorkClient.back_up(localWorkClient, 1000)
                    processWorkData = init_process(
                            localWorkClient, localWorkJson
                            )
                    localWorkData = get_local_data(processWorkData)
                    localWorkClient.update(localWorkData)
                    delete_tb('../cfg/del_tb.json', localWorkClient)
                print("批量处理完成")
                input('输入任意键回到菜单')
            case '7':
                clear()
                cross_cfg_json = init_data('../cfg/cross_db_cfg.json')
                print('跨服配置：')
                print(cross_cfg_json.out_data())

            case '0':
                door = 0
                print('系统关闭成功')
                exit()
            case _:
                print('请输入正确的数据')
                input('输入任意键回到菜单')
