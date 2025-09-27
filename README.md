## NuitkaHelper - Nuitka 打包辅助工具
![Python-3.8](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PySide6-6.9.1](https://img.shields.io/badge/PySide6-6.9.1-green.svg)
![Nuitka](https://img.shields.io/badge/Nuitka-%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC-orange.svg)

一个基于 PySide6 开发的图形化界面工具，用于简化 Nuitka Python 打包过程。无需记忆复杂的命令行参数，通过直观的图形界面即可完成专业的 Python 应用打包。

功能特点
🚀 核心功能
可视化配置：通过图形界面轻松配置 Nuitka 各项参数

实时输出：实时显示打包过程中的编译输出和错误信息

一键打包：点击按钮即可开始打包，无需手动输入命令

进度指示：实时显示打包进度状态

⚙️ 配置选项
打包模式：支持独立应用 (--standalone) 和单文件模式 (--onefile)

优化选项：LTO 优化、符号去除、断言移除等

插件支持：Tkinter、PySide6/PyQt6、NumPy、Pandas 等常用插件

包含文件：轻松添加需要包含的数据文件和目录

Windows 特供：控制台设置、管理员权限请求、自定义图标

🎯 用户体验
配置保存：自动保存和加载用户配置

历史记录：记录打包命令和结果

错误提示：详细的错误信息和解决方案提示

跨平台：支持 Windows、macOS、Linux 系统

# 使用方法
基本使用流程
选择源文件：点击"浏览"按钮选择要打包的 Python 文件

配置输出：设置输出目录和文件名

选择模式：根据需要选择独立应用或单文件模式

配置选项：在相应选项卡中设置优化、插件、包含文件等选项

开始打包：点击"开始打包"按钮，等待编译完成

界面说明
应用界面分为以下几个主要区域：

基本设置：源文件、输出目录、打包模式等基本配置

插件设置：启用各种 Python 插件和包含数据文件

高级设置：架构选择、调试选项、并行编译等高级配置

输出窗口：实时显示编译过程和结果信息

进度条：显示当前打包进度状态

# 配置说明
配置文件
应用会自动创建 config.json 文件保存用户配置，包括：

1.最近使用的源文件路径

2.输出目录设置

3.所有选项的当前状态

4.包含文件列表

# 自定义配置
您可以通过编辑 config.json 文件进行高级配置，或使用界面上的"导入/导出配置"功能。

项目结构
text
NuitkaHelper/
├── main.py                 # 主程序入口
├── nuitka_helper.ui        # 界面布局文件
├── config.json             # 配置文件（自动生成）
├── pyproject.toml          # 依赖包列表
├── ui.ui.                  # 
├── README.md               # 项目说明文档

# 常见问题
Q: 打包后的文件很大怎么办？
A: 可以尝试以下方法：
启用 LTO 优化
启用符号去除
移除不必要的插件
使用 UPX 压缩（需要额外安装）

Q: 打包后的应用无法运行？
A: 请检查：
是否包含了所有依赖文件
是否正确启用了相关插件
查看输出窗口的错误信息

Q: 如何添加数据文件？
A: 在"插件设置"选项卡的"包含数据"区域添加需要包含的文件或目录路径。

Q: 支持哪些 Python 版本？
A: 支持 Python 3.6 及以上版本，推荐使用 Python 3.8+。

贡献指南
我们欢迎各种形式的贡献！以下是参与项目的方式：

报告问题
如果您发现任何 bug 或有功能建议，请在 Issues 页面提交。


# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装开发依赖

致谢
感谢 Nuitka 项目提供了强大的 Python 打包能力

感谢 PySide6 提供了优秀的 GUI 框架

感谢 uv 提供了项目管理方案

感谢所有贡献者和用户的支持

支持与联系
如果您在使用过程中遇到问题或有任何建议，可以通过以下方式联系：

📧 邮箱：easonhellowin@outlook.com
