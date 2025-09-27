from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFileDialog, QApplication, QMessageBox, QMainWindow, QMenu
from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QCursor
from json import load, dump
import sys
import os

config :dict = {}


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load("ui.ui")
        # 连接信号和槽
        self.connect_signals()
        # 加载配置
        self.load_config()
        # 设置 includeList 的右键菜单
        self._setup_include_list_context_menu()

    def _setup_include_list_context_menu(self):
        """
        设置 includeList 的右键上下文菜单（仅删除）
        """
        self.ui.includeList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.includeList.customContextMenuRequested.connect(self._on_include_list_context_menu)

    def _on_include_list_context_menu(self, pos):
        """处理 includeList 的右键菜单请求"""
        context_menu = QMenu(self)
        delete_action = context_menu.addAction("删除")
        current_item = self.ui.includeList.itemAt(pos)
        delete_action.setEnabled(current_item is not None)
        action_selected = context_menu.exec(self.ui.includeList.mapToGlobal(pos))
        if action_selected == delete_action and current_item is not None:
            self._remove_include_item(current_item)

    def _remove_include_item(self, item):
        """
        从 includeList 中移除指定的项
        """
        self.ui.includeList.takeItem(self.ui.includeList.row(item))

    def connect_signals(self):
        """关联信号与槽"""
        self.ui.srcBtn.clicked.connect(self.srcBtn)
        self.ui.outBtn.clicked.connect(self.outBtn)
        self.ui.includeBtn.clicked.connect(self.includeBtn)
        self.ui.includeBtn_2.clicked.connect(self.includeBtn_2)
        self.ui.iconBtn.clicked.connect(self.iconBtn)
        self.ui.startBtn.clicked.connect(self.execute_nuitka_command)
        self.ui.stopBtn.clicked.connect(self.stop_process)
        self.ui.clearBtn.clicked.connect(self.ui.outputBrowser.clear)

    # 槽的实现
    def srcBtn(self):
        file, _ = QFileDialog.getOpenFileName(self.ui, "浏览",  "./", "Python源文件 (*.py *.pyi)")
        self.ui.srcEdit.setText(file)

    def outBtn(self):
        self.ui.outEdit.setText(QFileDialog.getExistingDirectory(self.ui, "浏览", "./"))

    def includeBtn(self):
        text = self.ui.includeEdit.text()
        different = True
        for i in range(self.ui.includeList.count()):
            item = self.ui.includeList.item(i).text()
            if text == item:
                different = False
                break
        if different:
            self.ui.includeList.addItem(text)

    def includeBtn_2(self):
        menu = QMenu(self)
        action_file = menu.addAction("选择文件...")
        action_dir = menu.addAction("选择目录...")
        action = menu.exec(QCursor.pos())  # 在光标位置弹出菜单

        if action == action_file:
            self._on_browse_include_file()
        elif action == action_dir:
            self._on_browse_include_dir()

    def _on_browse_include_file(self):
        """处理浏览文件按钮点击事件"""
        file_path, _ = QFileDialog.getOpenFileName(self,"选择要包含的文件","","All Files (*)")
        if file_path:
            self.ui.includeEdit.setText(file_path + " $file")

    def _on_browse_include_dir(self):
        """处理浏览目录按钮点击事件"""
        dir_path = QFileDialog.getExistingDirectory(self,"选择要包含的目录","",  QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if dir_path:
            self.ui.includeEdit.setText(dir_path + " $dir")

    def iconBtn(self):
        file, _ = QFileDialog.getOpenFileName(self.ui, "浏览", "", "图标文件 (*.ico)")
        self.ui.iconEdit.setText(file)

    def generate_nuitka_command(self):
        """
        根据 UI 控件状态生成 Nuitka 命令行指令

        返回:
            list: 包含 Nuitka 命令和参数的列表
        """
        command = ["python", "-m", "nuitka"]

        # 1. 基本设置
        # 源文件路径
        source_file = self.ui.srcEdit.text().strip()
        if not source_file:
            QMessageBox.warning(self, "错误", "请选择要编译的 Python 源文件")
            return None

        if not os.path.exists(source_file):
            QMessageBox.warning(self, "错误", f"源文件不存在: {source_file}")
            return None

        # 输出目录 - 使用等号形式避免参数错误
        output_dir = self.ui.outEdit.text().strip()
        if output_dir:
            # 检查路径是否有效
            if os.path.isdir(output_dir) or not os.path.exists(output_dir):
                command.append(f"--output-dir={output_dir}")
            else:
                QMessageBox.warning(self, "错误", f"输出路径不是有效的目录: {output_dir}")
                return None

        # 输出名称 - 使用等号形式
        output_name = self.ui.nameEdit.text().strip()
        if output_name:
            command.append(f"--output-filename={output_name}")

        # 2. 打包模式
        if self.ui.onefileRadio.isChecked():
            command.append("--onefile")
        else:
            command.append("--standalone")

        # 3. 优化选项
        if self.ui.ltoChk.isChecked():
            command.append("--lto=yes")

        if self.ui.stripChk.isChecked():
            command.append("--strip")

        if self.ui.removeOutputChk.isChecked():
            command.append("--remove-output")

        if self.ui.noassertChk.isChecked():
            command.append("--no-asserts")

        # 4. 操作系统选项
        if self.ui.winConsoleChk.isChecked():
            command.append("--windows-console-mode=disable")

        if self.ui.winUacAdminChk.isChecked():
            command.append("--windows-uac-admin")

        # 5. 插件设置
        plugins = []
        if self.ui.tkInterChk.isChecked():
            plugins.append("tk-inter")
        if self.ui.qtChk.isChecked():
            plugins.append("pyside6")
        if self.ui.numpyChk.isChecked():
            plugins.append("numpy")
        if self.ui.pandasChk.isChecked():
            plugins.append("pandas")
        if self.ui.djangoChk.isChecked():
            plugins.append("django")
        if self.ui.multiprocessingChk.isChecked():
            plugins.append("multiprocessing")

        for plugin in plugins:
            command.append(f"--enable-plugin={plugin}")

        # 6. 包含数据
        for i in range(self.ui.includeList.count()):
            include_item = self.ui.includeList.item(i).text().strip()
            if include_item:
                if "$file" in include_item:
                    command.append(f"--include-data-files={include_item.split(" $file")[0]}={os.path.basename(include_item.split(" $file")[0])}")
                if "$dir" in include_item:
                    print(os.path.basename(include_item))
                    command.append(f" --include-data-dir={include_item.split(" $dir")[0]}={os.path.basename(include_item.split(" $dir")[0])}")


        # 7. 架构设置
        # arch = self.ui.archCmb.currentText()
        # if arch != "自动检测":
        #     command.append(f"--arch={arch}")

        # 8. 调试选项
        if self.ui.showProgressChk.isChecked():
            command.append("--show-progress")

        if self.ui.showMemoryChk.isChecked():
            command.append("--show-memory")

        if self.ui.verboseChk.isChecked():
            command.append("--verbose")

        # 9. 其他选项
        # 并行作业数
        jobs = self.ui.jobsSpin.value()
        if jobs > 1:
            command.append(f"--jobs={jobs}")

        # 图标文件
        icon_file = self.ui.iconEdit.text().strip()
        if icon_file and os.path.exists(icon_file):
            command.append(f"--windows-icon-from-ico={icon_file}")

        # 10. 添加源文件路径（必须放在最后）
        command.append(source_file)

        return command

    def execute_nuitka_command(self):
        """执行 Nuitka 编译命令"""
        command = self.generate_nuitka_command()
        if command is None:
            return

        # 将命令转换为字符串用于显示
        command_str = " ".join(command)
        self.ui.outputBrowser.append(f"执行命令: {command_str}")
        self.ui.outputBrowser.append("-" * 50)

        # 更新进度条为不确定模式
        self.ui.progressBar.setRange(0, 0)

        # 禁用开始按钮，启用停止按钮
        self.ui.startBtn.setEnabled(False)
        self.ui.stopBtn.setEnabled(True)

        # 执行命令（这里需要之前提到的实时输出逻辑）
        # 假设你已经实现了 run_nuitka_command 方法来处理命令执行和实时输出
        self.run_nuitka_command(command)

    def run_nuitka_command(self, command):
        """
        执行 Nuitka 命令并实时显示输出

        参数:
            command: 要执行的命令列表
        """
        # 这里使用之前讨论的实时输出方法
        # 例如使用 QProcess 或 subprocess.Popen 配合线程

        try:
            # 创建进程
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.finished.connect(self.process_finished)

            # 启动进程
            self.process.start(command[0], command[1:])

        except Exception as e:
            self.ui.outputBrowser.append(f"执行命令时出错: {str(e)}")
            self.ui.progressBar.setRange(0, 100)
            self.ui.progressBar.setValue(0)
            self.ui.startBtn.setEnabled(True)
            self.ui.stopBtn.setEnabled(False)

    def handle_stdout(self):
        """
        处理标准输出
        """
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf-8", errors="replace")
        self.ui.outputBrowser.append(stdout)

    def handle_stderr(self):
        """
        处理标准错误
        """
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf-8", errors="replace")
        # 错误信息用红色显示
        self.ui.outputBrowser.append(f'<span style="color: red;">{stderr}</span>')

    def process_finished(self, exit_code, exit_status):
        """
        进程完成处理
        """
        # 恢复进度条
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(100)

        # 恢复按钮状态
        self.ui.startBtn.setEnabled(True)
        self.ui.stopBtn.setEnabled(False)

        # 显示完成信息
        if exit_code == 0:
            self.ui.outputBrowser.append("\n<span style=\"color: green;\">Nuitka 编译成功完成</span>")
            QMessageBox.information(self, "成功", "Nuitka 编译成功完成")
        else:
            self.ui.outputBrowser.append(f"\n编译失败，退出码: {exit_code}")
            QMessageBox.critical(self, "错误", f"Nuitka 编译失败，退出码: {exit_code}")

    def stop_process(self):
        """
        停止正在运行的进程
        """
        if hasattr(self, 'process') and self.process.state() == QProcess.Running:
            self.process.terminate()
            # 等待一段时间，如果进程没有终止，则强制杀死
            if not self.process.waitForFinished(2000):
                self.process.kill()

            self.ui.outputBrowser.append("\n编译过程已被用户终止")
            self.ui.progressBar.setRange(0, 100)
            self.ui.progressBar.setValue(0)
            self.ui.startBtn.setEnabled(True)
            self.ui.stopBtn.setEnabled(False)

    def load_config(self):
        """
        读取配置文件并初始化UI控件
        """
        try:
            with open("config.json", "r", encoding='utf-8') as f:
                global config
                config = load(f)
            # 基本设置
            if 'source_file' in config:
                self.ui.srcEdit.setText(config['source_file'])

            if 'output_dir' in config:
                self.ui.outEdit.setText(config['output_dir'])

            if 'output_name' in config:
                self.ui.nameEdit.setText(config['output_name'])

            # 打包模式
            if 'mode' in config:
                if config['mode'] == 'standalone':
                    self.ui.standaloneRadio.setChecked(True)
                elif config['mode'] == 'onefile':
                    self.ui.onefileRadio.setChecked(True)

            # 优化选项
            if 'optimization' in config:
                opts = config['optimization']
                self.ui.ltoChk.setChecked(opts.get('lto', False))
                self.ui.stripChk.setChecked(opts.get('strip', False))
                self.ui.removeOutputChk.setChecked(opts.get('remove_output', False))
                self.ui.noassertChk.setChecked(opts.get('no_asserts', False))

            # 操作系统选项
            if 'os_options' in config:
                os_opts = config['os_options']
                self.ui.winConsoleChk.setChecked(os_opts.get('windows_console', False))
                self.ui.winUacAdminChk.setChecked(os_opts.get('windows_uac_admin', False))

            # 插件设置
            if 'plugins' in config:
                plugins = config['plugins']
                self.ui.tkInterChk.setChecked(plugins.get('tk_inter', False))
                self.ui.qtChk.setChecked(plugins.get('qt', False))
                self.ui.numpyChk.setChecked(plugins.get('numpy', False))
                self.ui.pandasChk.setChecked(plugins.get('pandas', False))
                self.ui.djangoChk.setChecked(plugins.get('django', False))
                self.ui.multiprocessingChk.setChecked(plugins.get('multiprocessing', False))

            # 包含数据
            if 'include_files' in config:
                self.ui.includeList.clear()
                for file_path in config['include_files']:
                    self.ui.includeList.addItem(file_path)

            # Python选项
            if 'python_options' in config:
                py_opts = config['python_options']

            # 调试选项
            if 'debug_options' in config:
                debug_opts = config['debug_options']
                self.ui.showProgressChk.setChecked(debug_opts.get('show_progress', False))
                self.ui.showMemoryChk.setChecked(debug_opts.get('show_memory', False))
                self.ui.verboseChk.setChecked(debug_opts.get('verbose', False))

            # 其他选项
            if 'other_options' in config:
                other_opts = config['other_options']

            # 并行作业数
            if 'jobs' in other_opts:
                self.ui.jobsSpin.setValue(other_opts['jobs'])

            # 图标文件
            if 'icon_file' in other_opts:
                self.ui.iconEdit.setText(other_opts['icon_file'])

        except Exception as e:
            QMessageBox.critical(self.ui, "错误", f"加载配置失败！错误信息：{e}")
            sys.exit(1)

    def save_config(self):
        """保存当前设置到配置文件"""
        config = {
            'source_file': self.ui.srcEdit.text(),
            'output_dir': self.ui.outEdit.text(),
            'output_name': self.ui.nameEdit.text(),
            'mode': 'standalone' if self.ui.standaloneRadio.isChecked() else 'onefile',
            'optimization': {
                'lto': self.ui.ltoChk.isChecked(),
                'strip': self.ui.stripChk.isChecked(),
                'remove_output': self.ui.removeOutputChk.isChecked(),
                'no_asserts': self.ui.noassertChk.isChecked()
            },
            'os_options': {
                'windows_console': self.ui.winConsoleChk.isChecked(),
                'windows_uac_admin': self.ui.winUacAdminChk.isChecked()
            },
            'plugins': {
                'tk_inter': self.ui.tkInterChk.isChecked(),
                'qt': self.ui.qtChk.isChecked(),
                'numpy': self.ui.numpyChk.isChecked(),
                'pandas': self.ui.pandasChk.isChecked(),
                'django': self.ui.djangoChk.isChecked(),
                'multiprocessing': self.ui.multiprocessingChk.isChecked()
            },
            'include_files': [self.ui.includeList.item(i).text() for i in range(self.ui.includeList.count())],
            'debug_options': {
                'show_progress': self.ui.showProgressChk.isChecked(),
                'show_memory': self.ui.showMemoryChk.isChecked(),
                'verbose': self.ui.verboseChk.isChecked()
            },
            'other_options': {
                'jobs': self.ui.jobsSpin.value(),
                'icon_file': self.ui.iconEdit.text()
            }
        }

        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                dump(config, f, indent=4, ensure_ascii=False)
            print("配置保存成功")
        except Exception as e:
            QMessageBox.critical(self.ui, "错误", f"保存配置时出错: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    app =QApplication()
    app.setStyle("windows11")
    gui = GUI()
    gui.ui.show()
    app.exec()
    reply = QMessageBox.question(gui.ui, "退出", "是否保存当前配置？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes:
        gui.save_config()

