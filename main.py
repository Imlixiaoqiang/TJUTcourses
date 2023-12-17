from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import *
from fuction import *
from PyQt5.QtGui import QFont, QIcon


class WorkerThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, li, username, password):
        super().__init__()
        self.s = return_ss()
        self.li = li
        self.username = username
        self.password = password


    def checkLoginStatus(self):
        self.update_signal.emit(f"{check_login()}")
        if not check_login():
            login(self.username, self.password)
            self.s = return_ss()
            self.update_signal.emit("您已重新连接~")

    def run(self):

        while True:
            self.checkLoginStatus()
            for l in self.li:
                if l[1] == '公共选修课':
                    params = {
                        'method': 'handleQxgxk',
                        'jxbid': l[0],
                        'glJxbid': '',
                        'xkzy': '1'
                    }
                    ss = self.s.get('http://xk.tjut.edu.cn/xsxk/xkOper.xk', headers=headers, params=params).json()
                    self.update_signal.emit(f"{ss['message']}")
                else:
                    params = {
                        'method': 'handleTykxk',
                        'jxbid': l[0],
                        'glJxbid': '',
                        'xkzy': '1'
                    }
                    ss = self.s.get('http://xk.tjut.edu.cn/xsxk/xkOper.xk', headers=headers, params=params).json()
                    self.update_signal.emit(f"{ss['message']}")


class Main(QWidget):
    def __init__(self, username, password):
        super().__init__()
        self.initUI(username, password)
        self.thread = None
        self.setWindowIcon(QIcon("D:/桌面/TJUT选课/1.ico"))
    def initUI(self, username, password):
        self.setWindowTitle('TJUT公选课抢课软件')

        layout = QVBoxLayout()
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.checkLoginStatus(username, password))
        self.timer.start(10000)  # 10000毫秒，即10秒
        self.createMainTable(username, password)
        self.createSearchBox()
        self.searchBox.setFixedHeight(45)
        self.createInfoTable()
        self.createContextMenu()
        self.createButton(username, password)
        self.outputArea = QTextEdit(self)
        self.outputArea.setReadOnly(True)
        self.outputArea.setFontPointSize(15)
        self.outputArea.append('输出区')

        layout.addWidget(self.searchBox)
        font1 = QFont()
        font2 = QFont()
        font1.setPixelSize(30)
        font2.setPixelSize(22)
        # 添加一个标签并设置内容
        welcome_label = QLabel(
            f'{user()} 欢迎使用本软件，上方为所有公选课和体育课，下方为你要抢的课程，双击即可添加到下方')
        welcome_label.setFont(font2)

        j = xjd()
        x = QLabel(f'选课阶段：{j[0]}\n选课模式：{j[2]}\n选课策略：{j[1]}\n开始时间：{j[3]}\n结束时间：{j[4]}')
        x.setFont(font1)
        # 添加 MainTable 到水平布局中
        hbox = QHBoxLayout()
        hbox.addWidget(self.mainTable)
        hbox.addWidget(x)
        hbox.setStretchFactor(self.mainTable, 2)
        hbox.setStretchFactor(x, 1)
        layout.addLayout(hbox)
        layout.addWidget(welcome_label)
        h = QHBoxLayout()
        h.addWidget(self.infoTable)
        h.addWidget(self.outputArea)
        h.setStretchFactor(self.infoTable, 2)
        h.setStretchFactor(self.outputArea, 1)
        layout.addLayout(h)
        layout.addWidget(self.addButton)

        self.setLayout(layout)
        self.setFixedSize(1500, 1000)
        self.center()

    def checkLoginStatus(self, username, password):
        self.outputArea.append(f"登录状态：{check_login()}")
        if not check_login():
            login(username, password)

    def createButton(self, username, password):
        self.addButton = QPushButton('开始抢课', self)
        self.addButton.setFixedHeight(50)
        self.addButton.clicked.connect(lambda: self.toggle_grab_classes(username, password))

    def toggle_grab_classes(self, username, password):
        if self.addButton.text() == '开始抢课':
            self.grabClasses(username, password)
        else:
            self.stop_grab_classes(username, password)

    def stop_grab_classes(self, username, password):
        try:
            if self.thread and self.thread.isRunning():
                self.thread.terminate()
                self.thread.wait()
            self.addButton.setText('开始抢课')
            self.addButton.clicked.disconnect()
            self.addButton.clicked.connect(lambda: self.grabClasses(username, password))
            self.timer.start()
        except Exception as e:
            self.update_status(f'错误: {str(e)}')

    def grabClasses(self, username, password):
        try:

            info_column_data = [(self.infoTable.item(row, 0).text(), self.infoTable.item(row, 4).text()) for row in
                                range(self.infoTable.rowCount())]
            if len(info_column_data) != 0:
                self.addButton.setText('取消抢课')
                self.addButton.clicked.disconnect()
                self.addButton.clicked.connect(lambda: self.stop_grab_classes(username, password))
                self.outputArea.append(f'你要选的课是{info_column_data}')
                self.outputArea.append('开始抢课！')
                self.timer.stop()
                self.thread = WorkerThread(info_column_data, username, password)
                self.thread.update_signal.connect(self.update_status)
                self.thread.start()
            else:
                QMessageBox.warning(self, '错误', '选课不能为空')
        except Exception as e:
            self.update_status(f'Error: {str(e)}')

    def update_status(self, status):
        # 接收线程发来的消息并更新UI
        self.outputArea.append(f'Status: {status}')

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        # 计算窗口居中的坐标
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        # 移动窗口到屏幕中间
        self.move(x, y)

    def createMainTable(self, username, password):
        data = refresh_table(username, password)
        self.mainTable = QTableWidget(self)
        self.mainTable.setRowCount(len(data))
        self.mainTable.setColumnCount(5)
        self.mainTable.setHorizontalHeaderLabels(['课程lid码', '课程代码', '课程名称', '老师', '课程类型'])

        for row in range(len(data)):
            for col in range(5):
                item = QTableWidgetItem(data[row][col])
                item.setFlags(item.flags() ^ 2)  # Make items not editable
                self.mainTable.setItem(row, col, item)

        self.mainTable.cellDoubleClicked.connect(self.addToInfoTable)
        self.mainTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def createSearchBox(self):
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText('搜索想要的课程...')
        self.searchBox.textChanged.connect(self.searchTable)

    def createInfoTable(self):
        self.infoTable = QTableWidget(self)
        self.infoTable.setRowCount(0)  # Initialize with 0 rows
        self.infoTable.setColumnCount(5)
        self.infoTable.setHorizontalHeaderLabels(['课程lid码', '课程代码', '课程名称', '老师', '课程类型'])
        self.infoTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def createContextMenu(self):
        self.contextMenu = QMenu(self)
        delete_action = QAction("删除课程", self)
        delete_action.triggered.connect(self.deleteFromInfoTable)
        self.contextMenu.addAction(delete_action)
        self.infoTable.setContextMenuPolicy(3)  # ContextMenuPolicy for right-click
        self.infoTable.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, pos):
        self.contextMenu.exec_(self.infoTable.mapToGlobal(pos))

    def searchTable(self):
        search_text = self.searchBox.text().lower()

        for row in range(self.mainTable.rowCount()):
            for col in range(self.mainTable.columnCount()):
                item = self.mainTable.item(row, col)
                if search_text in item.text().lower():
                    self.mainTable.setRowHidden(row, False)
                    break
            else:
                self.mainTable.setRowHidden(row, True)

    def addToInfoTable(self, row):
        # 获取选中行的所有项
        selected_items = [self.mainTable.item(row, c) for c in range(self.mainTable.columnCount())]

        # 检查是否在infoTable中已存在相同行
        if self.isRowInInfoTable(selected_items):
            return

        # 在infoTable中插入一行
        row_position = self.infoTable.rowCount()
        self.infoTable.insertRow(row_position)

        # 将选中行的所有项复制到infoTable中
        for col_idx, item in enumerate(selected_items):
            new_item = QTableWidgetItem(item.text())
            new_item.setFlags(new_item.flags() ^ 2)  # Make items not editable
            self.infoTable.setItem(row_position, col_idx, new_item)
        self.infoTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def isRowInInfoTable(self, selected_items):
        # 遍历infoTable，检查是否存在相同行
        for row in range(self.infoTable.rowCount()):
            existing_items = [self.infoTable.item(row, c).text() for c in range(self.infoTable.columnCount())]
            if existing_items == [item.text() for item in selected_items]:
                return True
        return False

    def deleteFromInfoTable(self):
        current_row = self.infoTable.currentRow()
        if current_row != -1:
            self.infoTable.removeRow(current_row)
