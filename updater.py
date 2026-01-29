import requests
import json
import os
import sys
import time
import threading
import zipfile
import shutil

CURRENT_VERSION = "2.0.0"
GITHUB_REPO = "Wyl-cmd/JM_Downloader"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

class Updater:
    def __init__(self, current_version=CURRENT_VERSION):
        self.current_version = current_version
        self.latest_version = None
        self.download_url = None
        self.changelog = None
        self.update_available = False

    def check_for_updates(self):
        try:
            response = requests.get(GITHUB_API_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.latest_version = data.get('tag_name', '').replace('v', '')
                self.download_url = self._get_download_url(data)
                self.changelog = data.get('body', '')
                
                print(f"当前版本: {self.current_version}")
                print(f"最新版本: {self.latest_version}")
                
                if self._is_newer_version(self.latest_version, self.current_version):
                    self.update_available = True
                    return True, "发现新版本！"
                else:
                    return False, "已是最新版本"
            else:
                return False, f"检查更新失败: HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"网络错误: {str(e)}"
        except Exception as e:
            return False, f"检查更新时出错: {str(e)}"

    def _get_download_url(self, release_data):
        assets = release_data.get('assets', [])
        for asset in assets:
            name = asset.get('name', '').lower()
            if name.endswith('.exe'):
                return asset.get('browser_download_url')
        return None

    def _is_newer_version(self, latest, current):
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            for i in range(min(len(latest_parts), len(current_parts))):
                if latest_parts[i] > current_parts[i]:
                    return True
                elif latest_parts[i] < current_parts[i]:
                    return False
            return len(latest_parts) > len(current_parts)
        except:
            return False

    def download_update(self, progress_callback=None):
        if not self.download_url:
            return False, "没有找到下载链接"
        
        try:
            response = requests.get(self.download_url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            filename = f"JM_Downloader_v{self.latest_version}.exe"
            filepath = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(), filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if progress_callback:
                            progress = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                            progress_callback(progress, downloaded_size, total_size)
            
            return True, filepath
        except Exception as e:
            return False, f"下载更新失败: {str(e)}"

    def install_update(self, filepath, callback=None):
        try:
            current_exe = sys.executable if getattr(sys, 'frozen', False) else None
            
            if current_exe and os.path.exists(current_exe):
                backup_path = current_exe + '.bak'
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                shutil.move(current_exe, backup_path)
                print(f"已备份旧版本到: {backup_path}")
            
            new_exe_dir = os.path.dirname(filepath)
            new_exe_name = os.path.basename(filepath)
            target_path = os.path.join(new_exe_dir, 'JM_Downloader.exe')
            
            if os.path.exists(target_path):
                os.remove(target_path)
            
            shutil.move(filepath, target_path)
            print(f"新版本已安装到: {target_path}")
            
            if callback:
                callback(True, "更新安装成功！")
            return True, "更新安装成功"
        except Exception as e:
            if callback:
                callback(False, f"安装更新失败: {str(e)}")
            return False, f"安装更新失败: {str(e)}"

    def restart_application(self):
        try:
            exe_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd(), 'JM_Downloader.exe')
            if os.path.exists(exe_path):
                os.startfile(exe_path)
                sys.exit(0)
        except Exception as e:
            print(f"重启失败: {str(e)}")

def check_update_thread(label_widget, on_update_complete=None):
    def check():
        label_widget.configure(text="正在检查更新...")
        updater = Updater()
        has_update, message = updater.check_for_updates()
        
        if has_update:
            label_widget.configure(text=f"发现新版本 {updater.latest_version}")
            if on_update_complete:
                on_update_complete(updater, True, message)
        else:
            label_widget.configure(text=message)
            if on_update_complete:
                on_update_complete(None, False, message)
    
    thread = threading.Thread(target=check)
    thread.start()
    return thread

def download_update_thread(updater, label_widget, progress_label=None, on_download_complete=None):
    def download():
        label_widget.configure(text="正在下载更新...")
        
        def progress_callback(progress, downloaded, total):
            if progress_label:
                progress_label.configure(text=f"下载进度: {progress:.1f}% ({downloaded}/{total} bytes)")
        
        success, result = updater.download_update(progress_callback=progress_callback)
        
        if success:
            label_widget.configure(text="下载完成，正在安装...")
            if on_download_complete:
                on_download_complete(updater, result)
        else:
            label_widget.configure(text=f"下载失败: {result}")
            if on_download_complete:
                on_download_complete(None, False, result)
    
    thread = threading.Thread(target=download)
    thread.start()
    return thread

def install_update_thread(updater, filepath, label_widget, on_install_complete=None):
    def install():
        label_widget.configure(text="正在安装更新...")
        
        def callback(success, message):
            if success:
                label_widget.configure(text=message)
                if on_install_complete:
                    on_install_complete(True, message)
            else:
                label_widget.configure(text=f"安装失败: {message}")
                if on_install_complete:
                    on_install_complete(False, message)
        
        success, result = updater.install_update(filepath, callback=callback)
    
    thread = threading.Thread(target=install)
    thread.start()
    return thread
