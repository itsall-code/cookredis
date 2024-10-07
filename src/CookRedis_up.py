import os
import process
import get_redis
from pyjson import Json
from pipeline import Pipeline


class RedisManager:
    def __init__(self, config_path):
        self.json = Json(config_path)
        self.json.read_json_file()
        self.redis_client = self.get_client()

    def get_client(self):
        redis_data = self.json.get_redis()
        client = get_redis.Get_redis(
            redis_data['host'],
            redis_data['port'],
            redis_data['db'],
            redis_data['password']
        )
        client.create_connection()
        return client


class DataProcessor:
    def __init__(self, client, json):
        self.client = client
        self.json = json

    def process_data(self):
        self.client.get_data(self.json.json_data['account'])
        server_data = self.json.get_server()
        preLogin = self.json.json_data['preLogin']
        process_data = process.Process(
            self.client.data,
            server_data['platform'],
            server_data['group'],
            preLogin
        )
        process_data.get_keys()
        process_data.get_values()
        return process_data


class DataManager:
    def __init__(self):
        self.local_manager = RedisManager('../cfg/local_db_cfg.json')
        self.pipeline = Pipeline('../pipeline')

    @staticmethod
    def clear_console():
        os.system('cls')

    @staticmethod
    def examine(prompt):
        return input(prompt) == '1'

    def display_menu(self):
        while True:
            self.clear_console()
            print("请检查下面的配置与你的服务器配置是否一致")
            self.local_manager.json.out_data()
            choice = input("\n请选择操作:\n"
                           "1. 导入其他库到本服库\n"
                           "2. 备份本服库到其他库\n"
                           "3. 本地化账户数据\n"
                           "4. 删除 db{}\n"
                           "5. 重新初始化\n"
                           "6. 批量本地化操作\n"
                           "0. 退出\n".format(self.local_manager.json.redis_data['db']))

            actions = {
                '1': self.import_data,
                '2': self.backup_data,
                '3': self.localize_data,
                '4': self.delete_db,
                '5': self.reinitialize_data,
                '6': self.batch_localization,
                '0': self.exit_program
            }

            action = actions.get(choice)
            if action:
                action()
            else:
                print('请输入正确的数据')
                input('输入任意键回到菜单')

    def import_data(self):
        self.clear_console()
        source_manager = RedisManager('../cfg/source_db_cfg.json')
        print("请检查下面的配置与源数据库的Redis配置是否一致")
        source_manager.json.out_data()

        if self.examine("确认一致后，是否继续导入？\n1.是\t2.否\n请选择:"):
            source_manager.redis_client.back_up(self.local_manager.redis_client, 1000)
        else:
            print("本次无进行拉取数据操作")
        input('输入任意键回到菜单')

    def backup_data(self):
        self.clear_console()
        backup_manager = RedisManager('../cfg/backup_db_cfg.json')
        print("请检查下面的配置与备份数据库的Redis配置是否一致")
        backup_manager.json.out_data()

        if self.examine("确认一致后，是否继续备份？\n1.是\t2.否\n请选择:"):
            self.local_manager.redis_client.back_up(backup_manager.redis_client, 1000)
        else:
            print("本次无进行备份数据操作")
        input('输入任意键回到菜单')

    def localize_data(self):
        self.clear_console()
        if self.examine("确认一致后，是否继续本地化账户数据？\n1.是\t2.否\n请选择:"):
            processor = DataProcessor(self.local_manager.redis_client, self.local_manager.json)
            process_data = processor.process_data()
            local_data = process_data.get_local_data()
            self.local_manager.redis_client.deleta_key('db')
            self.local_manager.redis_client.update(local_data)
            print("数据已本地化成功，部分数据如下:")
            self.local_manager.redis_client.out_data()
        else:
            print("本次无进行本地化操作")
        input('输入任意键回到菜单')

    def delete_db(self):
        self.clear_console()
        print(f"该操作会删除 db{self.local_manager.json.redis_data['db']}")

        if self.examine("确认一致后，是否继续删除？\n1.是\t2.否\n请选择:"):
            self.local_manager.redis_client.delete_db()
            print(f"删除 db{self.local_manager.json.redis_data['db']} 成功")
        else:
            print(f"本次未删除 db{self.local_manager.json.redis_data['db']}")
        input('输入任意键回到菜单')

    def reinitialize_data(self):
        self.clear_console()
        print("数据重新初始化")
        self.local_manager = RedisManager('../cfg/local_db_cfg.json')
        input('输入任意键回到菜单')

    def batch_localization(self):
        self.clear_console()
        print("批量处理多个配置文件")

        for process_path in self.pipeline.folders:
            local_path = process_path.joinpath('local_db_cfg.json')
            source_path = process_path.joinpath('source_db_cfg.json')
            local_manager = RedisManager(local_path)
            source_manager = RedisManager(source_path)

            source_manager.redis_client.back_up(local_manager.redis_client, 1000)
            processor = DataProcessor(local_manager.redis_client, local_manager.json)
            local_data = processor.process_data().get_local_data()
            local_manager.redis_client.update(local_data)

        print("批量处理完成")
        input('输入任意键回到菜单')

    @staticmethod
    def exit_program():
        print('系统关闭成功')
        exit()


if __name__ == '__main__':
    data_manager = DataManager()
    data_manager.display_menu()

