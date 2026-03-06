from pathlib import Path


# 批量导入数据并处理的流水线
class Pipeline:

    # 类初始化，预热获取流水线中的配置
    def __init__(self, path):
        self.directory = Path(path)

    def get_cfg_folders(self):
        folders = [
                folder for folder in self.directory.iterdir()
                if folder.is_dir()
                ]
        self.folders = folders
        return self.folders

    def joinpath(self, filename):
        return self.folders.joinpath(filename)

    def out_folders(self):
        for folder in self.folders:
            print(folder.joinpath('cfg.json'))


if __name__ == '__main__':
    test = Pipeline("../pipeline")
    test.get_cfg_folders()
    test.out_folders()
