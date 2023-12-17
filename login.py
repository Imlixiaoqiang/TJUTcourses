from sys import exit, argv
from fuction import login
from PyQt5.QtWidgets import *
from main import Main


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('登录界面')
        self.init_ui()

    def init_ui(self):
        # 创建控件
        self.label_username = QLabel('学号:')
        self.label_password = QLabel('密码:')
        self.edit_username = QLineEdit()
        self.edit_password = QLineEdit()
        self.btn_login = QPushButton('登录')
        self.edit_password.returnPressed.connect(self.login_clicked)
        self.btn_login.setDefault(True)  # 设置默认按钮，使其在按下回车键时触发

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.edit_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.edit_password)
        layout.addWidget(self.btn_login)

        # 设置按钮点击事件
        self.btn_login.clicked.connect(self.login_clicked)

        # 将布局应用到窗口
        self.setLayout(layout)

        # 设置窗口固定大小
        self.setFixedSize(400, 300)

        # 将窗口移动到屏幕中间
        self.center()

        # 设置样式表
        self.setStyleSheet("""
            QLabel {
                font-size: 22px;  /* 修改学号、密码标签的字体大小为20 */
            }
            QLineEdit {
                padding: 8px;
                font-size: 22px;  /* 修改输入框中文字的字体大小为18 */
            }
            QPushButton {
                padding: 15px;
                font-size: 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def center(self):
        # 获取屏幕的尺寸
        screen = QDesktopWidget().screenGeometry()

        # 获取窗口的尺寸
        window_size = self.geometry()

        # 计算窗口居中的坐标
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2

        # 移动窗口到屏幕中间
        self.move(x, y)

    def login_clicked(self):
        # 处理登录按钮点击事件
        username = self.edit_username.text()
        password = self.edit_password.text()
        # 在这里调用登录函数，处理登录逻辑
        try:
            response = login(username, password)  # 假设登录成功
            if response == '':
                QMessageBox.information(self, '登录成功', '登录成功')
                self.close()
                self.main_window = Main(username, password)
                self.main_window.show()
            else:
                QMessageBox.warning(self, '登录失败', response)
        except Exception as e:
            # 发生异常，弹出错误信息框
            QMessageBox.warning(self, '登录失败', str(e))


if __name__ == '__main__':
    app = QApplication(argv)
    login_window = LoginWindow()
    login_window.show()

    exit(app.exec_())
