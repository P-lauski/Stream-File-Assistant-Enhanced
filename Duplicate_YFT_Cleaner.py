# Acknowledgement:
# This tool is inspired by and references the FiveM project.
# GitHub Repository: https://github.com/citizenfx/fivem/blob/master/code/components/citizen-server-impl/src/ResourceStreamComponent.cpp
import os
import hashlib
import pyperclip
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed
import struct
import sys
import subprocess
from pathlib import Path

class HiYftGuiTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate YFT Cleaner by pgonintwitch")
        self.root.geometry("1150x800")  # Adjust window size to accommodate more components
        self.root.resizable(True, True)  # Allow resizing

        # Initialize variables
        self.root_directory = tk.StringVar()
        self.deletable_files = []
        self.total_files = 0
        self.processed_files = 0
        self.current_language = "en"
        self.sort_column = None
        self.sort_reverse = False
        self.right_clicked_row = None  # New variable to record the row right-clicked

        # Define multilingual dictionary
        self.translations = {
            "en": {
                "title": "Duplicate YFT Cleaner by pgonintwitch",
                "root_dir_label": "Root Directory:",
                "browse_button": "Browse...",
                "scan_button": "Start Scan",
                "progress_label": "Progress: {}/{}",
                "select_all_button": "Select All",
                "select_column": "Select",
                "model_name_column": "Model Name",
                "path_column": "File Path",
                "size_column": "Size (MB)",
                "status_column": "Status",
                "copy_clipboard_button": "Copy List to Clipboard",
                "save_file_button": "Save List to File",
                "delete_files_button": "Delete Selected Files",
                "status_ready": "Ready",
                "status_scanning": "Scanning...",
                "status_completed": "Scan Completed.",
                "status_error": "Error:",
                "confirm_delete_title": "Confirm Deletion",
                "confirm_delete_message": "Are you sure you want to delete the selected {} files?",
                "success_delete": "Successfully deleted {} files.",
                "error_delete": "Failed to delete the following files:\n{}",
                "info_no_files": "No files available.",
                "info_no_selected": "No files selected.",
                "info_copy_success": "File list copied to clipboard.",
                "info_copy_fail": "Failed to copy to clipboard.",
                "info_save_success": "File list saved to {}.",
                "info_save_fail": "Failed to save file list.",
                "language_label": "Language:",
                "status_ok": "OK",
                "status_warning": "Warning",
                "status_critical": "Critical",
                "oversized_warning": "Oversized assets can and WILL lead to streaming issues (such as models not loading/rendering).",
                "view_folder": "View Folder",
            },
            "zh_TW": {
                "title": "YFT 檢查管理工具 by pgonintwitch",
                "root_dir_label": "根目錄路徑：",
                "browse_button": "瀏覽...",
                "scan_button": "開始掃描",
                "progress_label": "進度：{}/{}",
                "select_all_button": "全選",
                "select_column": "選擇",
                "model_name_column": "模型名稱",
                "path_column": "檔案路徑",
                "size_column": "大小 (MB)",
                "status_column": "狀態",
                "copy_clipboard_button": "複製清單到剪貼簿",
                "save_file_button": "保存清單到文件",
                "delete_files_button": "刪除選定的檔案",
                "status_ready": "準備就緒",
                "status_scanning": "掃描中...",
                "status_completed": "掃描完成。",
                "status_error": "錯誤：",
                "confirm_delete_title": "確認刪除",
                "confirm_delete_message": "確定要刪除選定的 {} 個檔案嗎？",
                "success_delete": "已成功刪除 {} 個檔案。",
                "error_delete": "無法刪除以下檔案：\n{}",
                "info_no_files": "沒有可用的檔案。",
                "info_no_selected": "沒有選擇檔案。",
                "info_copy_success": "檔案清單已複製到剪貼簿。",
                "info_copy_fail": "無法複製到剪貼簿。",
                "info_save_success": "檔案清單已保存到 {}。",
                "info_save_fail": "無法保存檔案清單。",
                "language_label": "語言：",
                "status_ok": "正常",
                "status_warning": "警告",
                "status_critical": "危急",
                "oversized_warning": "Oversized assets can and WILL lead to streaming issues (such as models not loading/rendering).",
                "view_folder": "打開資料夾",
            },
            "zh_CN": {
                "title": "YFT 检查与管理工具 by pgonintwitch",
                "root_dir_label": "根目录路径：",
                "browse_button": "浏览...",
                "scan_button": "开始扫描",
                "progress_label": "进度：{}/{}",
                "select_all_button": "全选",
                "select_column": "选择",
                "model_name_column": "模型名称",
                "path_column": "文件路径",
                "size_column": "大小 (MB)",
                "status_column": "状态",
                "copy_clipboard_button": "复制清单到剪贴板",
                "save_file_button": "保存清单到文件",
                "delete_files_button": "删除选定的文件",
                "status_ready": "准备就绪",
                "status_scanning": "扫描中...",
                "status_completed": "扫描完成。",
                "status_error": "错误：",
                "confirm_delete_title": "确认删除",
                "confirm_delete_message": "确定要删除选定的 {} 个文件吗？",
                "success_delete": "已成功删除 {} 个文件。",
                "error_delete": "无法删除以下文件：\n{}",
                "info_no_files": "没有可用的文件。",
                "info_no_selected": "没有选择文件。",
                "info_copy_success": "文件清单已复制到剪贴板。",
                "info_copy_fail": "无法复制到剪贴板。",
                "info_save_success": "文件清单已保存到 {}。",
                "info_save_fail": "无法保存文件清单。",
                "language_label": "语言：",
                "status_ok": "正常",
                "status_warning": "警告",
                "status_critical": "危急",
                "oversized_warning": "Oversized assets can and WILL lead to streaming issues (such as models not loading/rendering).",
                "view_folder": "打开文件夹",
            },
            "es": {
                "title": "Limpiador de YFT Duplicados por pgonintwitch",
                "root_dir_label": "Directorio Raíz:",
                "browse_button": "Examinar...",
                "scan_button": "Iniciar Escaneo",
                "progress_label": "Progreso: {}/{}",
                "select_all_button": "Seleccionar Todo",
                "select_column": "Seleccionar",
                "model_name_column": "Nombre del Modelo",
                "path_column": "Ruta del Archivo",
                "size_column": "Tamaño (MB)",
                "status_column": "Estado",
                "copy_clipboard_button": "Copiar Lista al Portapapeles",
                "save_file_button": "Guardar Lista en Archivo",
                "delete_files_button": "Eliminar Archivos Seleccionados",
                "status_ready": "Listo",
                "status_scanning": "Escaneando...",
                "status_completed": "Escaneo Completo.",
                "status_error": "Error:",
                "confirm_delete_title": "Confirmar Eliminación",
                "confirm_delete_message": "¿Está seguro de que desea eliminar los {} archivos seleccionados?",
                "success_delete": "Se han eliminado correctamente {} archivos.",
                "error_delete": "No se pudieron eliminar los siguientes archivos:\n{}",
                "info_no_files": "No hay archivos disponibles.",
                "info_no_selected": "No se han seleccionado archivos.",
                "info_copy_success": "Lista de archivos copiada al portapapeles.",
                "info_copy_fail": "No se pudo copiar al portapapeles.",
                "info_save_success": "Lista de archivos guardada en {}.",
                "info_save_fail": "No se pudo guardar la lista de archivos.",
                "language_label": "Idioma:",
                "status_ok": "OK",
                "status_warning": "Advertencia",
                "status_critical": "Crítico",
                "oversized_warning": "Oversized assets can and WILL lead to streaming issues (such as models not loading/rendering).",
                "view_folder": "Ver Carpeta",
            },
            # More languages can be added here
        }

        # Setup UI
        self.setup_ui()

    def translate(self, text_id, *args):
        text = self.translations.get(self.current_language, {}).get(text_id, text_id)
        if args:
            return text.format(*args)
        return text

    def setup_ui(self):
        # Styling
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Calibri', 12, 'bold'))
        style.configure("TButton", padding=6, font=('Calibri', 10))
        style.configure("TLabel", font=('Calibri', 10))
        style.configure("TCombobox", font=('Calibri', 10))

        # Directory selection area
        frame_top = ttk.Frame(self.root, padding=10)
        frame_top.pack(fill=tk.X)

        lbl_dir = ttk.Label(frame_top, text=self.translate("root_dir_label"))
        lbl_dir.pack(side=tk.LEFT, padx=(0, 5))

        entry_dir = ttk.Entry(frame_top, textvariable=self.root_directory, width=60)
        entry_dir.pack(side=tk.LEFT, padx=(0, 5))

        btn_browse = ttk.Button(frame_top, text=self.translate("browse_button"), command=self.browse_directory)
        btn_browse.pack(side=tk.LEFT)

        # Language selection area
        lbl_language = ttk.Label(frame_top, text=self.translate("language_label"))
        lbl_language.pack(side=tk.LEFT, padx=(20, 5))

        self.language_var = tk.StringVar(value="en")
        cmb_language = ttk.Combobox(
            frame_top, textvariable=self.language_var, state="readonly",
            values=list(self.translations.keys()), width=10
        )
        cmb_language.pack(side=tk.LEFT)
        cmb_language.bind("<<ComboboxSelected>>", self.change_language)

        # Scan button and progress bar
        frame_scan = ttk.Frame(self.root, padding=10)
        frame_scan.pack(fill=tk.X)

        btn_scan = ttk.Button(frame_scan, text=self.translate("scan_button"), command=self.start_scan)
        btn_scan.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(frame_scan, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=10)

        # Default display 0/0
        self.lbl_progress = ttk.Label(frame_scan, text=self.translate("progress_label", 0, 0))
        self.lbl_progress.pack(side=tk.LEFT)

        # Add "Select All" button frame, placed above the Treeview
        frame_select_all = ttk.Frame(self.root, padding=(10, 0))
        frame_select_all.pack(fill=tk.X)

        btn_select_all = ttk.Button(frame_select_all, text=self.translate("select_all_button"), command=self.select_all)
        btn_select_all.pack(anchor='w')  # Align to left

        # List display area
        frame_list = ttk.Frame(self.root, padding=10)
        frame_list.pack(fill=tk.BOTH, expand=True)

        columns = ("select", "model_name", "path", "size", "status")
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings", selectmode="none")
        self.tree.heading("select", text=self.translate("select_column"), command=lambda: self.sort_tree("select"))
        self.tree.heading("model_name", text=self.translate("model_name_column"), command=lambda: self.sort_tree("model_name"))
        self.tree.heading("path", text=self.translate("path_column"), command=lambda: self.sort_tree("path"))
        self.tree.heading("size", text=self.translate("size_column"), command=lambda: self.sort_tree("size"))
        self.tree.heading("status", text=self.translate("status_column"), command=lambda: self.sort_tree("status"))

        self.tree.column("select", width=80, anchor="center")
        self.tree.column("model_name", width=200, anchor="w")
        self.tree.column("path", width=400, anchor="w")
        self.tree.column("size", width=150, anchor="center")
        self.tree.column("status", width=200, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Enable column width adjustment
        self.tree.bind('<Button-1>', self.handle_click)
        self.tree.bind('<Button-3>', self.show_context_menu)

        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Action buttons area
        frame_actions = ttk.Frame(self.root, padding=10)
        frame_actions.pack(fill=tk.X)

        btn_copy = ttk.Button(frame_actions, text=self.translate("copy_clipboard_button"), command=self.copy_to_clipboard)
        btn_copy.pack(side=tk.LEFT, padx=5)

        btn_save = ttk.Button(frame_actions, text=self.translate("save_file_button"), command=self.save_to_file)
        btn_save.pack(side=tk.LEFT, padx=5)

        btn_delete = ttk.Button(frame_actions, text=self.translate("delete_files_button"), command=self.delete_selected_files)
        btn_delete.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status = tk.StringVar()
        self.status.set(self.translate("status_ready"))
        lbl_status = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor="w")
        lbl_status.pack(fill=tk.X, side=tk.BOTTOM)

        # Create right-click context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label=self.translate("view_folder"), command=self.view_folder)

    def change_language(self, event=None):
        selected_language = self.language_var.get()
        self.current_language = selected_language

        # Update all UI text
        self.root.title(self.translate("title"))
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        current_text = child.cget("text")
                        # Update progress or other texts
                        if "Progress" in current_text or "進度" in current_text or "Progreso" in current_text:
                            child.config(text=self.translate("progress_label", self.processed_files, self.total_files))
                        elif current_text in self.translations["en"].values() or \
                             current_text in self.translations["zh_TW"].values() or \
                             current_text in self.translations["es"].values() or \
                             current_text in self.translations["zh_CN"].values():
                            # Find corresponding key
                            for lang, trans in self.translations.items():
                                for key, value in trans.items():
                                    if current_text == value:
                                        child.config(text=self.translate(key))
                                        break
                    elif isinstance(child, ttk.Button):
                        current_text = child.cget("text")
                        for lang, trans in self.translations.items():
                            for key, value in trans.items():
                                if current_text == value:
                                    child.config(text=self.translate(key))
                                    break
        # Update table headers
        self.tree.heading("select", text=self.translate("select_column"))
        self.tree.heading("model_name", text=self.translate("model_name_column"))
        self.tree.heading("path", text=self.translate("path_column"))
        self.tree.heading("size", text=self.translate("size_column"))
        self.tree.heading("status", text=self.translate("status_column"))

        # Update action buttons
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.root.winfo_children()[0] and widget != self.root.winfo_children()[-1]:
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        current_text = child.cget("text")
                        for lang, trans in self.translations.items():
                            for key, value in trans.items():
                                if current_text == value:
                                    child.config(text=self.translate(key))
                                    break
        # Update context menu
        self.context_menu.entryconfig(0, label=self.translate("view_folder"))

    def select_all(self):
        for item in self.tree.get_children():
            self.tree.set(item, "select", "☑")

    def sort_tree(self, column):
        # Toggle sort order
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_column = column

        # Define a key function based on the column
        def sort_key(item):
            value = self.tree.set(item, column)
            if column == "size":
                try:
                    # Handle different size string formats
                    if '/' in value:
                        # PH:xx.xx/VR:yy.yy MB
                        parts = value.split('/')
                        return max(float(parts[0].split(':')[1]), float(parts[1].split(':')[1]))
                    else:
                        return float(value.split(' ')[0])
                except:
                    return 0.0
            return value.lower()

        sorted_items = sorted(self.tree.get_children(), key=sort_key, reverse=self.sort_reverse)
        for index, item in enumerate(sorted_items):
            self.tree.move(item, '', index)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.root_directory.set(directory)

    def start_scan(self):
        if not self.root_directory.get():
            messagebox.showwarning("Warning", self.translate("info_no_selected"))
            return

        if not os.path.isdir(self.root_directory.get()):
            messagebox.showerror("Error", self.translate("info_no_files"))
            return

        # Clear Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.deletable_files.clear()
        self.total_files = 0
        self.processed_files = 0
        self.progress["value"] = 0
        self.lbl_progress.config(text=self.translate("progress_label", self.processed_files, self.total_files))

        # Update status
        self.status.set(self.translate("status_scanning"))

        threading.Thread(target=self.scan_files, daemon=True).start()

    def scan_files(self):
        try:
            hi_yft_files = self.find_hi_yft_files(self.root_directory.get())
            unique_hi_yft_files = list(set(hi_yft_files))  # Remove duplicates
            self.total_files = len(unique_hi_yft_files)
            self.update_progress()

            results = []
            with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
                future_map = {executor.submit(self.process_file, f): f for f in unique_hi_yft_files}
                for future in as_completed(future_map):
                    r = future.result()
                    if r:
                        results.append(r)
                    self.processed_files += 1
                    self.update_progress()

            self.deletable_files = results
            self.populate_treeview(results)
            self.status.set(self.translate("status_completed"))
        except Exception as e:
            self.update_status(f"{self.translate('status_error')} {e}")

    def process_file(self, hi_file):
        """
        If the YFT is RSC7 (or RSC8...), use ConvertRSC7Size(rscPagesPhysical) / ConvertRSC7Size(rscPagesVirtual)
        and display as PH:xx.xx/VR:yy.yy MB.
        If not an RSC resource, display the actual file size.
        Finally, use the "maximum value" to determine the status (OK/Warning/Critical).
        """
        original_file = self.get_original_file(hi_file)
        if not original_file or not os.path.isfile(original_file):
            return None

        # Check if file contents are identical (hash)
        hi_hash = self.compute_file_hash(hi_file)
        org_hash = self.compute_file_hash(original_file)
        if not hi_hash or not org_hash or hi_hash != org_hash:
            return None

        # Try to read YFT header
        # rscVersion, rscPagesPhysical, rscPagesVirtual
        # If magic == RSC7(0x37435352) or RSC8(0x38435352), then isResource = true
        # Otherwise, fallback
        is_resource, physPages, virtPages = self.read_yft_header(hi_file)

        if is_resource:
            phys_size = self.convert_rsc7_size(physPages)
            virt_size = self.convert_rsc7_size(virtPages)
            # Convert to MB
            phys_mb = phys_size / (1024.0 * 1024.0)
            virt_mb = virt_size / (1024.0 * 1024.0)
            # Display both sizes
            size_str = f"PH:{phys_mb:.2f}/VR:{virt_mb:.2f} MB"

            # Use the maximum value to determine status
            max_mb = max(phys_mb, virt_mb)
            status = self.determine_status(max_mb)
            if status in [self.translate("status_warning"), self.translate("status_critical")]:
                status += f" - {self.translate('oversized_warning')}"
            return (hi_file, size_str, status)
        else:
            # If not an RSC resource, use the actual file size
            actual_size = os.path.getsize(hi_file)
            actual_mb = actual_size / (1024.0 * 1024.0)
            size_str = f"{actual_mb:.2f} MB"
            status = self.determine_status(actual_mb)
            if status in [self.translate("status_warning"), self.translate("status_critical")]:
                status += f" - {self.translate('oversized_warning')}"
            return (hi_file, size_str, status)

    def read_yft_header(self, file_path):
        """
        Returns: (is_resource, rscPagesPhysical, rscPagesVirtual)
        """
        try:
            with open(file_path, 'rb') as f:
                # According to C++ code, the first 16 bytes are:
                # magic (4 bytes), version (4 bytes), virtPages (4 bytes), physPages (4 bytes)
                header = f.read(16)
                if len(header) < 16:
                    return (False, 0, 0)
                magic, version, virtPages, physPages = struct.unpack('<IIII', header)
                # According to C++ code, magic values:
                # 0x37435352 -> RSC7
                # 0x05435352 -> RSC\x05
                # 0x38435352 -> RSC8
                if magic in [0x37435352, 0x38435352]:
                    # RSC7 / RSC8
                    return (True, physPages, virtPages)
                elif magic == 0x05435352:
                    # RSC\x05
                    return (True, version, virtPages)
                else:
                    return (False, 0, 0)
        except Exception as e:
            self.update_status(f"{self.translate('status_error')} {e}")
            return (False, 0, 0)

    def convert_rsc7_size(self, flags):
        """
        Corresponds to the C++ ConvertRSC7Size function
        """
        s0 = ((flags >> 27) & 0x1) << 0
        s1 = ((flags >> 26) & 0x1) << 1
        s2 = ((flags >> 25) & 0x1) << 2
        s3 = ((flags >> 24) & 0x1) << 3
        s4 = ((flags >> 17) & 0x7F) << 4
        s5 = ((flags >> 11) & 0x3F) << 5
        s6 = ((flags >> 7) & 0xF) << 6
        s7 = ((flags >> 5) & 0x3) << 7
        s8 = ((flags >> 4) & 0x1) << 8
        ss = (flags >> 0) & 0xF
        baseSize = 0x200 << ss
        size = baseSize * (s0 + s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8)
        return size

    def determine_status(self, size_mb):
        # Determine status based on size thresholds from the original source code
        # >64MB => critical, >32MB => warning, >16MB => warning, else => ok
        if size_mb > 64:
            return self.translate("status_critical")
        elif size_mb > 32:
            return self.translate("status_warning")
        elif size_mb > 16:
            return self.translate("status_warning")
        else:
            return self.translate("status_ok")

    def update_progress(self):
        if self.total_files > 0:
            progress_percent = (self.processed_files / self.total_files) * 100
            self.progress["value"] = progress_percent
            self.lbl_progress.config(text=self.translate("progress_label", self.processed_files, self.total_files))
            self.root.update_idletasks()

    def find_hi_yft_files(self, root_dir):
        """
        using pathlib and glob patterns to recursively find all '_hi.yft' files under 'stream' directories.
        Args:
            root_dir (str): root directory to start the search from.
        
        Returns:
            List[str]: a list of all found '_hi.yft' files。
        """
        hi_yft_files = []
        root = Path(root_dir)
        # using rglob to find all directories named 'stream'
        for stream_dir in root.rglob('stream'):
            if stream_dir.is_dir():
                # using glob to find all files named '*_hi.yft'
                for yft_file in stream_dir.glob('**/*_hi.yft'):
                    hi_yft_files.append(str(yft_file))
        return hi_yft_files
    def get_original_file(self, hi_file):
        dirpath, hi_filename = os.path.split(hi_file)
        base_name, ext = os.path.splitext(hi_filename)
        if '_hi' not in base_name.lower():
            return None
        original_base_name = base_name.lower().replace('_hi', '')
        original_filename = original_base_name + ext
        return os.path.join(dirpath, original_filename)

    def compute_file_hash(self, file_path):
        hash_func = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            self.update_status(f"{self.translate('status_error')} {e}")
            return None

    def populate_treeview(self, file_info_list):
        """
        file_info_list: [(filepath, size_str, status), ...]
        """
        for (file_path, size_str, status) in file_info_list:
            model_name = os.path.basename(file_path)
            path = os.path.dirname(file_path)
            self.tree.insert(
                "",
                tk.END,
                values=("☐", model_name, path, size_str, status),
                tags=(status,)
            )
            # Mark color based on status
            if status.startswith(self.translate("status_ok")):
                self.tree.item(self.tree.get_children()[-1], tags=("ok",))
                self.tree.tag_configure("ok", background="lightgreen")
            elif status.startswith(self.translate("status_warning")):
                self.tree.item(self.tree.get_children()[-1], tags=("warning",))
                self.tree.tag_configure("warning", background="yellow")
            elif status.startswith(self.translate("status_critical")):
                self.tree.item(self.tree.get_children()[-1], tags=("critical",))
                self.tree.tag_configure("critical", background="red")

    def handle_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        column = self.tree.identify_column(event.x)
        if column == "#1":  # 'select' column
            row_id = self.tree.identify_row(event.y)
            if row_id:
                current_value = self.tree.set(row_id, "select")
                new_value = "☑" if current_value == "☐" else "☐"
                self.tree.set(row_id, "select", new_value)

    def show_context_menu(self, event):
        # Ensure a row is clicked
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.right_clicked_row = row_id  # Record the right-clicked row
            self.context_menu.post(event.x_root, event.y_root)
        else:
            self.right_clicked_row = None  # Reset if not clicking on a row

    def view_folder(self):
        if self.right_clicked_row:
            # Use the right-clicked row to get the file path
            path = self.tree.set(self.right_clicked_row, "path")
            model_name = self.tree.set(self.right_clicked_row, "model_name")
            full_path = os.path.join(path, model_name)
            folder_path = os.path.dirname(full_path)
        else:
            # If no specific row is clicked, use selected files
            selected = self.get_selected_files()
            if not selected:
                messagebox.showinfo("Info", self.translate("info_no_selected"))
                return
            # Take the first selected file
            folder_path = os.path.dirname(selected[0])

        try:
            if sys.platform.startswith('darwin'):
                subprocess.call(['open', folder_path])
            elif os.name == 'nt':
                os.startfile(folder_path)
            elif os.name == 'posix':
                subprocess.call(['xdg-open', folder_path])
            else:
                messagebox.showerror("Error", "Unsupported OS.")
        except Exception as e:
            messagebox.showerror("Error", f"{self.translate('status_error')} {e}")

    def copy_to_clipboard(self):
        selected = self.get_selected_files()
        if not selected:
            messagebox.showinfo("Info", self.translate("info_no_selected"))
            return
        try:
            pyperclip.copy('\n'.join(selected))
            messagebox.showinfo("Success", self.translate("info_copy_success"))
        except pyperclip.PyperclipException as e:
            messagebox.showerror("Error", f"{self.translate('status_error')} {e}")

    def save_to_file(self):
        selected = self.get_selected_files()
        if not selected:
            messagebox.showinfo("Info", self.translate("info_no_selected"))
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title=self.translate("save_file_button")
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(selected))
                messagebox.showinfo("Success", self.translate("info_save_success", file_path))
            except Exception as e:
                messagebox.showerror("Error", f"{self.translate('status_error')} {e}")

    def get_selected_files(self):
        selected_files = []
        for item in self.tree.get_children():
            if self.tree.set(item, "select") == "☑":
                model_name = self.tree.item(item, "values")[1]
                path = self.tree.item(item, "values")[2]
                full_path = os.path.join(path, model_name)
                selected_files.append(full_path)
        return selected_files

    def delete_selected_files(self):
        selected_files = self.get_selected_files()
        if not selected_files:
            messagebox.showinfo("Info", self.translate("info_no_selected"))
            return

        confirm = messagebox.askyesno(
            self.translate("confirm_delete_title"),
            self.translate("confirm_delete_message", len(selected_files))
        )
        if not confirm:
            return

        deleted = []
        failed = []
        for fp in selected_files:
            try:
                os.remove(fp)
                deleted.append(fp)
                # Remove from Treeview
                for item in self.tree.get_children():
                    model_name = self.tree.item(item, "values")[1]
                    path = self.tree.item(item, "values")[2]
                    if os.path.join(path, model_name) == fp:
                        self.tree.delete(item)
                        break
            except Exception as e:
                failed.append((fp, str(e)))

        if deleted:
            messagebox.showinfo("Success", self.translate("success_delete", len(deleted)))
            self.deletable_files = [df for df in self.deletable_files if df[0] not in deleted]

        if failed:
            error_msg = "\n".join([f"{p}: {err}" for p, err in failed])
            messagebox.showerror("Error", self.translate("error_delete", error_msg))

        self.status.set(self.translate("status_completed"))

    def update_status(self, msg):
        self.status.set(msg)
        self.root.update_idletasks()


def main():
    root = tk.Tk()
    app = HiYftGuiTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
