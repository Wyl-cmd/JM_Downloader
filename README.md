# JM下载器

一个简单易用的漫画下载和PDF转换工具，支持下载漫画并自动转换为PDF格式方便阅读。

## 功能特点
- 输入漫画ID即可下载
- 支持批量下载多个漫画（使用 / 分隔ID）
- 自动将下载的漫画图片转换为PDF
- 提供PDF文件管理功能（查看、删除）
- 支持多种图片格式：.jpg, .jpeg, .png, .webp
- 自动处理RGBA模式图片（转换为白色背景）
- 支持打包为单文件可执行程序，无需安装Python环境
- 自动记录下载日志便于调试

## 安装指南

### 方法1：直接使用可执行文件
1. 前往发布页面下载最新的可执行文件
2. 双击运行即可使用

### 方法2：从源码运行
1. 克隆本仓库
```bash
https://github.com/yourusername/JMbenzi.git
cd JMbenzi
```
2. 安装依赖
```bash
pip install -r requirements.txt
```
3. 运行程序
```bash
python main.py
```

## 使用说明

### 单个漫画下载
1. 在输入框中输入漫画ID
2. 点击"开始下载并转换"按钮
3. 等待下载和转换完成
4. 点击"管理PDF文件"按钮可以查看和管理已下载的PDF

### 批量下载
1. 在输入框中输入多个漫画ID，使用 `/` 符号分隔
   - 例如：`123/456/789`
2. 点击"开始下载并转换"按钮
3. 程序会按顺序依次下载每个漫画，并显示当前下载进度
4. 下载完成后会自动转换为PDF格式

### PDF文件管理
1. 点击"管理PDF文件"按钮打开管理窗口
2. 单击选择PDF文件
3. 双击打开PDF文件
4. 点击"删除选中的PDF及文件夹"可同时删除PDF和原始图片文件夹
5. 点击"刷新列表"可更新文件列表

## 注意事项
- 下载过程中请不要多次点击下载按钮，可能会导致线程中断
- 如遇下载未成功的情况，请关闭软件重新运行
- PDF管理功能中，双击列表项可打开PDF文件
- 程序会将漫画下载到当前运行目录
- 下载日志会保存到 `download_log.txt` 文件中，便于排查问题
- 如果PDF文件已存在，程序会自动跳过转换
- 程序会自动处理RGBA模式图片，将其转换为白色背景的RGB格式

## 致谢
- 感谢[jmcomic](https://github.com/xxx/jmcomic)库提供的漫画下载功能
- 感谢[Pillow](https://python-pillow.org/)库提供的图片处理功能
- 感谢[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)库提供的GUI支持

## 联系方式
- QQ群：1154539255
- 二群：521292550
- B站主页：[https://space.bilibili.com/397706571](https://space.bilibili.com/397706571)
- B站小号：[https://space.bilibili.com/3546591426251062](https://space.bilibili.com/3546591426251062)