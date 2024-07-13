import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox
import importlib.util

# 动态加载脚本文件
def load_script(script_path):
    spec = importlib.util.spec_from_file_location("module.name", script_path)
    script_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script_module)
    return script_module

class SimpleGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # 加载脚本
        self.redis_script = load_script('./get_redis.py')
        self.process_script = load_script('./process.py')

    def initUI(self):
        self.setWindowTitle('集成功能的PyQt5 GUI')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.button = QPushButton('执行任务', self)
        self.button.clicked.connect(self.on_click)

        layout.addWidget(self.button)

        self.setLayout(layout)

    def on_click(self):
        # 假设get_redis.py有一个函数get_data，process.py有一个函数process_data
        try:
            data = self.redis_script.get_data()
            processed_data = self.process_script.process_data(data)
            QMessageBox.information(self, '结果', f'处理结果: {processed_data}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'发生错误: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = SimpleGUI()
    gui.show()
    sys.exit(app.exec_())

