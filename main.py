import sys
import jmcomic, os, time, yaml
from PIL import Image
import customtkinter as ctk
import tkinter as tk
import threading
import shutil
import webbrowser
from updater import Updater, check_update_thread, download_update_thread, install_update_thread

def all2pdf(input_folder, pdfpath, pdfname):
    start_time = time.time()
    path = input_folder
    if not isinstance(path, str):
        raise ValueError("path 必须是一个字符串")

    zimulu = []  # 子目录（里面为image）
    image = []  # 子目录图集
    sources = []  # pdf格式的图
    supported_formats = [".jpg", ".jpeg", ".png", ".webp"]  # 支持的图片格式

    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                try:
                    zimulu.append(int(entry.name))
                except ValueError:
                    print(f"跳过非整数的子目录名: {entry.name}")
            if entry.is_file() and any(entry.name.lower().endswith(ext) for ext in supported_formats):
                image.append(os.path.join(path, entry.name))

    # 对数字进行排序
    zimulu.sort()

    for i in zimulu:
        sub_path = os.path.join(path, str(i))
        with os.scandir(sub_path) as entries:
            for entry in entries:
                if entry.is_dir():
                    print("这一级不应该有自录")
                if entry.is_file() and any(entry.name.lower().endswith(ext) for ext in supported_formats):
                    image.append(os.path.join(sub_path, entry.name))

    if len(image) == 0:
        print(f"没有找到{supported_formats}格式文件，不生成PDF")
        return f"没有找到{supported_formats}格式文件，不生成PDF"

    # 检查第一张图片是否为支持的格式
    first_image_supported = any(image[0].lower().endswith(ext) for ext in supported_formats)
    if first_image_supported:
        output = Image.open(image[0])
        image.pop(0)
    else:
        print(f"没有找到{supported_formats}格式文件，不生成PDF")
        return f"没有找到{supported_formats}格式文件，不生成PDF"

    for file in image:
        if any(file.lower().endswith(ext) for ext in supported_formats):
            img_file = Image.open(file)
            if img_file.mode == "RGBA":
                # 处理透明背景，将其转换为白色
                background = Image.new("RGB", img_file.size, (255, 255, 255))
                background.paste(img_file, mask=img_file.split()[3])  # 3 is the alpha channel
                img_file = background
            elif img_file.mode != "RGB":
                img_file = img_file.convert("RGB")
            sources.append(img_file)

    pdf_file_path = os.path.join(pdfpath, pdfname)
    if not pdf_file_path.endswith(".pdf"):
        pdf_file_path += ".pdf"
    output.save(pdf_file_path, "pdf", save_all=True, append_images=sources)
    end_time = time.time()
    run_time = end_time - start_time
    return f"运行时间：{run_time:.2f} 秒"

def download_and_convert(entry_widget, label_widget):
    label_widget.configure(text="状态: 下载中...")  # 更新状态信息
    manga_id = entry_widget.get()
    manga_ids = [manga_id]

    # 使用程序所在目录作为下载目录
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_path = os.getcwd()
    # 记录详细调试信息到日志文件
    log_path = os.path.join(base_path, 'download_log.txt')
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 打包状态: {getattr(sys, 'frozen', False)}\n")
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 程序路径: {sys.executable}\n")
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 当前下载路径: {base_path}\n")
    # 同时输出到控制台和日志
    log_message = f"打包状态: {getattr(sys, 'frozen', False)}"
    print(log_message)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {log_message}\n")

    log_message = f"程序路径: {sys.executable}"
    print(log_message)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {log_message}\n")

    log_message = f"当前下载路径: {base_path}"
    print(log_message)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {log_message}\n")

    for manga_id in manga_ids:  # 使用manga_id避免与内置id冲突
        try:
            # 不使用config，使用默认配置
            # 添加调试信息
            log_message = f"准备下载漫画ID {manga_id} 到目录: {base_path}"
            print(log_message)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {log_message}\n")
            # 指定下载目录
            # 使用正确的参数名，假设为download_dir
              # 创建默认下载选项并设置下载目录
            option = jmcomic.JmOption.default()
            # 复制选项并修改下载目录
            new_option = option.copy_option()
            new_option.dir_rule.base_dir = base_path
            jmcomic.download_album(manga_id, option=new_option)
            log_message = f"漫画ID {manga_id} 下载完成，保存到: {base_path}"
            print(log_message)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {log_message}\n")
        except Exception as e:
            log_message = f"下载漫画ID {manga_id} 时出错: {e}"
            print(log_message)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {log_message}\n")
            label_widget.configure(text=f"下载漫画ID {manga_id} 时出错: {e}")
            continue

    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    with os.scandir(base_path) as entries:
        for entry in entries:
            if entry.is_dir():
                pdf_file_path = os.path.join(base_path, entry.name + ".pdf")
                if os.path.exists(pdf_file_path):
                    print("文件：《%s》 已存在，跳过" % entry.name)
                    label_widget.configure(text=f"文件：《{entry.name}》 已存在，跳过")
                    continue
                else:
                    print("开始转换：%s " % entry.name)
                    label_widget.configure(text=f"开始转换：{entry.name}")
                    result = all2pdf(os.path.join(base_path, entry.name), base_path, entry.name)
                    label_widget.configure(text=result)
    label_widget.configure(text="状态: 空闲")  # 更新状态信息

def run_download_thread(entry_widget, label_widget):
    thread = threading.Thread(target=download_and_convert, args=(entry_widget, label_widget))
    thread.start()

def open_pdf(filename):
    if os.name == 'nt':  # 适用于Windows
        os.startfile(filename)
    # 删除了不支持的部分

def delete_pdf_and_folder(pdf_name, status_label):
    # 使用与下载功能相同的方法获取基础路径
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_path = os.getcwd()

    if pdf_name:  # 检查是否选中了文件
        pdf_file_path = os.path.join(base_path, pdf_name + ".pdf")
        folder_path = os.path.join(base_path, pdf_name)

        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)
            print(f"已删除PDF文件: {pdf_file_path}")
            status_label.configure(text=f"已删除PDF文件: {pdf_file_path}")
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"已删除文件夹: {folder_path}")
            status_label.configure(text=f"已删除文件夹: {folder_path}")
    else:  # 没有选中文件
        print("没有选中的PDF文件")
        status_label.configure(text="没有选中的PDF文件")

    refresh_pdf_list()

def refresh_pdf_list():
    global pdf_list  # 确保使用的是全局变量
    global manage_window  # 确保能访问到窗口
    if pdf_list is None and manage_window is not None:
        pdf_list = tk.Listbox(manage_window, selectmode=tk.SINGLE)
    pdf_list.delete(0, tk.END)
    # 使用与下载功能相同的方法获取基础路径
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_path = os.getcwd()

    with os.scandir(base_path) as entries:
        for entry in entries:
            if entry.is_dir():
                pdf_file_path = os.path.join(base_path, entry.name + ".pdf")
                if os.path.exists(pdf_file_path):
                    pdf_list.insert(tk.END, entry.name)

def manage_pdfs():
    def on_double_click(event):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            pdf_name = widget.get(selection[0])
            pdf_file_path = os.path.join(base_path, pdf_name + ".pdf")
            open_pdf(pdf_file_path)

    global pdf_list
    # 使用与下载功能相同的方法获取基础路径
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_path = os.getcwd()

    global manage_window
    manage_window = ctk.CTkToplevel(root)
    manage_window.title("管理PDF文件")
    manage_window.geometry("400x500")

    pdf_list = tk.Listbox(manage_window, selectmode=tk.SINGLE)
    pdf_list.pack(pady=20, padx=10, fill=tk.BOTH, expand=True)
    pdf_list.bind("<Double-1>", on_double_click)

    refresh_button = ctk.CTkButton(manage_window, text="刷新列表", command=refresh_pdf_list)
    refresh_button.pack(pady=10, padx=10)

    # 添加状态标签
    status_label = ctk.CTkLabel(manage_window, text="")
    status_label.pack(pady=10, padx=10)

    delete_button = ctk.CTkButton(manage_window, text="删除选中的PDF及文件夹", command=lambda: delete_pdf_and_folder(pdf_list.get(tk.ANCHOR), status_label))
    delete_button.pack(pady=10, padx=10)

    refresh_pdf_list()

def show_help():
    help_text = """
by：K_空想科技
注意！
单击选择，双击打开。
软件有概率出现下载未成功的情况，此时请关闭软件重新运行。
另外请不要在下载过程中多次点击下载，会导致线程中断（我没做多线程下载，以后会做吧，鸽了）
其余信息：
QQ群：1154539255（有啥问题直接进去问！）
QQ群号，B站主页也有，可以直接复制，我懒得做功能了。
冷知识：以下链接直接点击即可跳转。
"""
    help_window = ctk.CTkToplevel(root)
    help_window.title("帮助")
    help_window.geometry("600x400")

    help_label = ctk.CTkLabel(help_window, text=help_text, justify=tk.LEFT)
    help_label.pack(pady=20, padx=10)

    bilibili_label = ctk.CTkLabel(help_window, text="我的B站主页", justify=tk.LEFT, cursor="hand2")
    bilibili_label.pack(pady=(0, 10), padx=10)
    bilibili_label.bind("<Button-1>", lambda event: webbrowser.open_new("https://space.bilibili.com/397706571"))

def check_update():
    updater = Updater()
    has_update, message = updater.check_for_updates()
    
    update_window = ctk.CTkToplevel(root)
    update_window.title("检查更新")
    update_window.geometry("500x400")
    
    status_label = ctk.CTkLabel(update_window, text=message)
    status_label.pack(pady=20, padx=10)
    
    if has_update:
        version_label = ctk.CTkLabel(update_window, text=f"发现新版本: {updater.latest_version}", font=("Arial", 14, "bold"))
        version_label.pack(pady=10, padx=10)
        
        changelog_text = ctk.CTkTextbox(update_window, height=150, width=450)
        changelog_text.insert("0.0", updater.changelog or "暂无更新日志")
        changelog_text.pack(pady=10, padx=10)
        
        def on_update_complete(updater_obj, success, msg):
            if success:
                status_label.configure(text=msg)
                if isinstance(updater_obj, Updater):
                    def on_install_complete(success, msg):
                        if success:
                            restart_btn = ctk.CTkButton(update_window, text="重启程序", command=lambda: updater_obj.restart_application())
                            restart_btn.pack(pady=10, padx=10)
                        status_label.configure(text=msg)
                    install_update_thread(updater_obj, msg, status_label, on_install_complete=on_install_complete)
            else:
                status_label.configure(text=msg)
        
        download_btn = ctk.CTkButton(update_window, text="下载更新", command=lambda: download_update_thread(updater, status_label, on_download_complete=on_update_complete))
        download_btn.pack(pady=10, padx=10)
    else:
        close_btn = ctk.CTkButton(update_window, text="关闭", command=update_window.destroy)
        close_btn.pack(pady=10, padx=10)

# 自定义设置：
# 下载目录已硬编码为程序当前目录，无需加载配置文件
# load_config = jmcomic.JmOption.from_file(config)

# 创建窗口
root = ctk.CTk()
root.title("JM下载器")
root.geometry("400x300")

# 创建顶部框架（用于放置更新按钮）
top_frame = ctk.CTkFrame(root)
top_frame.pack(side="top", fill="x", padx=10, pady=5)

# 创建一个检查更新按钮（小巧，放在左上角）
update_button = ctk.CTkButton(top_frame, text="🔄", width=40, height=30, font=("Arial", 16), command=check_update)
update_button.pack(side="left", padx=5)

# 创建一个标题标签（放在右上角）
title_label = ctk.CTkLabel(top_frame, text="JM下载器", font=("Arial", 14, "bold"))
title_label.pack(side="right", padx=5)

# 创建一个输入框
entry = ctk.CTkEntry(root, placeholder_text="请输入漫画ID")
entry.pack(pady=20, padx=10)

# 创建一个按钮
button = ctk.CTkButton(root, text="开始下载并转换", command=lambda: run_download_thread(entry, label))
button.pack(pady=10, padx=10)

# 创建一个标签用于显示结果和状态信息
label = ctk.CTkLabel(root, text="状态: 空闲")
label.pack(pady=10, padx=10)

# 创建一个管理按钮
manage_button = ctk.CTkButton(root, text="管理PDF文件", command=manage_pdfs)
manage_button.pack(pady=10, padx=10)

# 创建一个帮助按钮
help_button = ctk.CTkButton(root, text="帮助", command=show_help)
help_button.pack(pady=10, padx=10)

# 运行窗口
root.mainloop()
