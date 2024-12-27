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
        self.root.title("Stream files assistant by pgonintwitch")
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
        self.right_clicked_row = None  # Variable to record the row right-clicked

        # Variables for Stream Duplicate Checker
        self.stream_root_directory = tk.StringVar()
        self.duplicate_files = {}
        self.total_stream_files = 0
        self.processed_stream_files = 0

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
                # Stream Duplicate Checker Translations
                "stream_tab": "Stream Duplicate Checker",
                "stream_root_dir_label": "Stream Root Directory:",
                "stream_browse_button": "Browse...",
                "stream_scan_button": "Scan for Duplicates",
                "stream_progress_label": "Progress: {}/{}",
                "stream_duplicate_file_column": "Duplicate File Name",
                "stream_locations_column": "Locations",
                "stream_select_all_button": "Select All",
                "stream_copy_clipboard_button": "Copy Duplicates to Clipboard",
                "stream_save_file_button": "Save Duplicates to File",
                "stream_delete_duplicates_button": "Delete Selected Duplicates",
                "stream_status_ready": "Ready",
                "stream_status_scanning": "Scanning...",
                "stream_status_completed": "Scan Completed.",
                "stream_status_error": "Error:",
                "stream_confirm_delete_title": "Confirm Deletion",
                "stream_confirm_delete_message": "Are you sure you want to delete the selected duplicate files?",
                "stream_success_delete": "Successfully deleted {} duplicate files.",
                "stream_error_delete": "Failed to delete the following duplicate files:\n{}",
                "stream_info_no_duplicates": "No duplicate files found.",
                "stream_info_no_selected": "No duplicate files selected.",
                "stream_info_copy_success": "Duplicate file list copied to clipboard.",
                "stream_info_copy_fail": "Failed to copy duplicate file list to clipboard.",
                "stream_info_save_success": "Duplicate file list saved to {}.",
                "stream_info_save_fail": "Failed to save duplicate file list.",
                "stream_select_column": "Select",
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
                # Stream Duplicate Checker Translations
                "stream_tab": "Stream 重複檔案檢查",
                "stream_root_dir_label": "Stream 根目錄路徑：",
                "stream_browse_button": "瀏覽...",
                "stream_scan_button": "掃描重複檔案",
                "stream_progress_label": "進度：{}/{}",
                "stream_duplicate_file_column": "重複檔案名稱",
                "stream_locations_column": "所在位置",
                "stream_select_all_button": "全選",
                "stream_copy_clipboard_button": "複製重複檔案到剪貼簿",
                "stream_save_file_button": "保存重複檔案到文件",
                "stream_delete_duplicates_button": "刪除選定的重複檔案",
                "stream_status_ready": "準備就緒",
                "stream_status_scanning": "掃描中...",
                "stream_status_completed": "掃描完成。",
                "stream_status_error": "錯誤：",
                "stream_confirm_delete_title": "確認刪除",
                "stream_confirm_delete_message": "確定要刪除選定的重複檔案嗎？",
                "stream_success_delete": "已成功刪除 {} 個重複檔案。",
                "stream_error_delete": "無法刪除以下重複檔案：\n{}",
                "stream_info_no_duplicates": "未發現重複檔案。",
                "stream_info_no_selected": "未選擇任何重複檔案。",
                "stream_info_copy_success": "重複檔案清單已複製到剪貼簿。",
                "stream_info_copy_fail": "無法將重複檔案清單複製到剪貼簿。",
                "stream_info_save_success": "重複檔案清單已保存到 {}。",
                "stream_info_save_fail": "無法保存重複檔案清單。",
                "stream_select_column": "選擇",
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
                # Stream Duplicate Checker Translations
                "stream_tab": "Stream 重复文件检查",
                "stream_root_dir_label": "Stream 根目录路径：",
                "stream_browse_button": "浏览...",
                "stream_scan_button": "扫描重复文件",
                "stream_progress_label": "进度：{}/{}",
                "stream_duplicate_file_column": "重复文件名称",
                "stream_locations_column": "所在位置",
                "stream_select_all_button": "全选",
                "stream_copy_clipboard_button": "复制重复文件到剪贴板",
                "stream_save_file_button": "保存重复文件到文件",
                "stream_delete_duplicates_button": "删除选定的重复文件",
                "stream_status_ready": "准备就绪",
                "stream_status_scanning": "扫描中...",
                "stream_status_completed": "扫描完成。",
                "stream_status_error": "错误：",
                "stream_confirm_delete_title": "确认删除",
                "stream_confirm_delete_message": "确定要删除选定的重复文件吗？",
                "stream_success_delete": "已成功删除 {} 个重复文件。",
                "stream_error_delete": "无法删除以下重复文件：\n{}",
                "stream_info_no_duplicates": "未发现重复文件。",
                "stream_info_no_selected": "未选择任何重复文件。",
                "stream_info_copy_success": "重复文件清单已复制到剪贴板。",
                "stream_info_copy_fail": "无法将重复文件清单复制到剪贴板。",
                "stream_info_save_success": "重复文件清单已保存到 {}。",
                "stream_info_save_fail": "无法保存重复文件清单。",
                "stream_select_column": "选择",
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
                # Stream Duplicate Checker Translations
                "stream_tab": "Verificador de Duplicados Stream",
                "stream_root_dir_label": "Directorio Raíz de Stream:",
                "stream_browse_button": "Examinar...",
                "stream_scan_button": "Escanear Duplicados",
                "stream_progress_label": "Progreso: {}/{}",
                "stream_duplicate_file_column": "Nombre de Archivo Duplicado",
                "stream_locations_column": "Ubicaciones",
                "stream_select_all_button": "Seleccionar Todo",
                "stream_copy_clipboard_button": "Copiar Duplicados al Portapapeles",
                "stream_save_file_button": "Guardar Duplicados en Archivo",
                "stream_delete_duplicates_button": "Eliminar Duplicados Seleccionados",
                "stream_status_ready": "Listo",
                "stream_status_scanning": "Escaneando...",
                "stream_status_completed": "Escaneo Completo.",
                "stream_status_error": "Error:",
                "stream_confirm_delete_title": "Confirmar Eliminación",
                "stream_confirm_delete_message": "¿Está seguro de que desea eliminar los archivos duplicados seleccionados?",
                "stream_success_delete": "Se han eliminado correctamente {} archivos duplicados.",
                "stream_error_delete": "No se pudieron eliminar los siguientes archivos duplicados:\n{}",
                "stream_info_no_duplicates": "No se encontraron archivos duplicados.",
                "stream_info_no_selected": "No se seleccionaron archivos duplicados.",
                "stream_info_copy_success": "Lista de archivos duplicados copiada al portapapeles.",
                "stream_info_copy_fail": "No se pudo copiar la lista de archivos duplicados al portapapeles.",
                "stream_info_save_success": "Lista de archivos duplicados guardada en {}.",
                "stream_info_save_fail": "No se pudo guardar la lista de archivos duplicados.",
                "stream_select_column": "Seleccionar",
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

        # Create Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: YFT Cleaner
        self.tab_yft = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_yft, text=self.translate("title"))

        # Tab 2: Stream Duplicate Checker
        self.tab_stream = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_stream, text=self.translate("stream_tab"))

        # Setup YFT Cleaner UI in tab_yft
        self.setup_yft_tab()

        # Setup Stream Duplicate Checker UI in tab_stream
        self.setup_stream_tab()

        # Status bar
        self.status = tk.StringVar()
        self.status.set(self.translate("status_ready"))
        lbl_status = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor="w")
        lbl_status.pack(fill=tk.X, side=tk.BOTTOM)

        # Create right-click context menus
        self.yft_context_menu = tk.Menu(self.root, tearoff=0)
        self.yft_context_menu.add_command(label=self.translate("view_folder"), command=self.view_folder)

        self.stream_context_menu = tk.Menu(self.root, tearoff=0)
        # Entries will be dynamically added based on the clicked item

    def setup_yft_tab(self):
        # Directory selection area
        frame_top = ttk.Frame(self.tab_yft, padding=10)
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
        frame_scan = ttk.Frame(self.tab_yft, padding=10)
        frame_scan.pack(fill=tk.X)

        btn_scan = ttk.Button(frame_scan, text=self.translate("scan_button"), command=self.start_scan)
        btn_scan.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(frame_scan, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=10)

        # Default display 0/0
        self.lbl_progress = ttk.Label(frame_scan, text=self.translate("progress_label", 0, 0))
        self.lbl_progress.pack(side=tk.LEFT)

        # Add "Select All" button frame, placed above the Treeview
        frame_select_all = ttk.Frame(self.tab_yft, padding=(10, 0))
        frame_select_all.pack(fill=tk.X)

        btn_select_all = ttk.Button(frame_select_all, text=self.translate("select_all_button"), command=self.select_all)
        btn_select_all.pack(anchor='w')  # Align to left

        # List display area
        frame_list = ttk.Frame(self.tab_yft, padding=10)
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

        # Enable column width adjustment and context menu
        self.tree.bind('<Button-1>', self.handle_click)
        self.tree.bind('<Button-3>', self.show_yft_context_menu)

        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Action buttons area
        frame_actions = ttk.Frame(self.tab_yft, padding=10)
        frame_actions.pack(fill=tk.X)

        btn_copy = ttk.Button(frame_actions, text=self.translate("copy_clipboard_button"), command=self.copy_to_clipboard)
        btn_copy.pack(side=tk.LEFT, padx=5)

        btn_save = ttk.Button(frame_actions, text=self.translate("save_file_button"), command=self.save_to_file)
        btn_save.pack(side=tk.LEFT, padx=5)

        btn_delete = ttk.Button(frame_actions, text=self.translate("delete_files_button"), command=self.delete_selected_files)
        btn_delete.pack(side=tk.LEFT, padx=5)

    def setup_stream_tab(self):
        # Directory selection area
        frame_top = ttk.Frame(self.tab_stream, padding=10)
        frame_top.pack(fill=tk.X)

        lbl_dir = ttk.Label(frame_top, text=self.translate("stream_root_dir_label"))
        lbl_dir.pack(side=tk.LEFT, padx=(0, 5))

        entry_dir = ttk.Entry(frame_top, textvariable=self.stream_root_directory, width=60)
        entry_dir.pack(side=tk.LEFT, padx=(0, 5))

        btn_browse = ttk.Button(frame_top, text=self.translate("stream_browse_button"), command=self.browse_stream_directory)
        btn_browse.pack(side=tk.LEFT)

        # Scan button and progress bar
        frame_scan = ttk.Frame(self.tab_stream, padding=10)
        frame_scan.pack(fill=tk.X)

        btn_scan = ttk.Button(frame_scan, text=self.translate("stream_scan_button"), command=self.start_stream_scan)
        btn_scan.pack(side=tk.LEFT)

        self.stream_progress = ttk.Progressbar(frame_scan, orient="horizontal", length=500, mode="determinate")
        self.stream_progress.pack(side=tk.LEFT, padx=10)

        # Default display 0/0
        self.stream_lbl_progress = ttk.Label(frame_scan, text=self.translate("stream_progress_label", 0, 0))
        self.stream_lbl_progress.pack(side=tk.LEFT)

        # Add "Select All" button frame, placed above the Treeview
        frame_select_all = ttk.Frame(self.tab_stream, padding=(10, 0))
        frame_select_all.pack(fill=tk.X)

        btn_select_all_stream = ttk.Button(frame_select_all, text=self.translate("stream_select_all_button"), command=self.select_all_stream)
        btn_select_all_stream.pack(anchor='w')  # Align to left

        # List display area
        frame_list = ttk.Frame(self.tab_stream, padding=10)
        frame_list.pack(fill=tk.BOTH, expand=True)

        stream_columns = ("select", "duplicate_file", "locations")
        self.stream_tree = ttk.Treeview(frame_list, columns=stream_columns, show="headings", selectmode="none")
        self.stream_tree.heading("select", text=self.translate("stream_select_column"), command=lambda: self.sort_stream_tree("select"))
        self.stream_tree.heading("duplicate_file", text=self.translate("stream_duplicate_file_column"), command=lambda: self.sort_stream_tree("duplicate_file"))
        self.stream_tree.heading("locations", text=self.translate("stream_locations_column"), command=lambda: self.sort_stream_tree("locations"))

        self.stream_tree.column("select", width=80, anchor="center")
        self.stream_tree.column("duplicate_file", width=300, anchor="w")
        self.stream_tree.column("locations", width=700, anchor="w")

        self.stream_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Enable column width adjustment and context menu
        self.stream_tree.bind('<Button-1>', self.handle_click_stream)
        self.stream_tree.bind('<Button-3>', self.show_stream_context_menu)

        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.stream_tree.yview)
        self.stream_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Action buttons area
        frame_actions = ttk.Frame(self.tab_stream, padding=10)
        frame_actions.pack(fill=tk.X)

        btn_copy = ttk.Button(frame_actions, text=self.translate("stream_copy_clipboard_button"), command=self.copy_stream_to_clipboard)
        btn_copy.pack(side=tk.LEFT, padx=5)

        btn_save = ttk.Button(frame_actions, text=self.translate("stream_save_file_button"), command=self.save_stream_to_file)
        btn_save.pack(side=tk.LEFT, padx=5)

        # I strongly recommend you use the context menu instead : )

        # btn_delete = ttk.Button(frame_actions, text=self.translate("stream_delete_duplicates_button"), command=self.delete_selected_stream_duplicates)
        # btn_delete.pack(side=tk.LEFT, padx=5)

    def change_language(self, event=None):
        selected_language = self.language_var.get()
        self.current_language = selected_language

        # Update Notebook tab titles
        self.notebook.tab(0, text=self.translate("title"))
        self.notebook.tab(1, text=self.translate("stream_tab"))

        # Update all UI text in YFT Cleaner tab
        self.update_yft_tab_language()

        # Update all UI text in Stream Duplicate Checker tab
        self.update_stream_tab_language()

        # Update status bar
        self.status.set(self.translate("status_ready"))

        # Update context menus
        self.yft_context_menu.entryconfig(0, label=self.translate("view_folder"))
        # Note: Stream context menu entries are dynamic and handled separately

    def update_yft_tab_language(self):
        # Update labels and buttons in YFT tab
        for widget in self.tab_yft.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        text_id = self.get_text_id(child.cget("text"))
                        if text_id:
                            if text_id == "root_dir_label":
                                child.config(text=self.translate("root_dir_label"))
                            elif text_id == "language_label":
                                child.config(text=self.translate("language_label"))
                    elif isinstance(child, ttk.Button):
                        text_id = self.get_text_id(child.cget("text"))
                        if text_id:
                            if text_id == "browse_button":
                                child.config(text=self.translate("browse_button"))
                            elif text_id == "scan_button":
                                child.config(text=self.translate("scan_button"))
                            elif text_id == "select_all_button":
                                child.config(text=self.translate("select_all_button"))
        # Update Treeview headers
        self.tree.heading("select", text=self.translate("select_column"))
        self.tree.heading("model_name", text=self.translate("model_name_column"))
        self.tree.heading("path", text=self.translate("path_column"))
        self.tree.heading("size", text=self.translate("size_column"))
        self.tree.heading("status", text=self.translate("status_column"))

        # Update Action buttons
        for widget in self.tab_yft.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.tab_yft.winfo_children()[0]:
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        text_id = self.get_text_id(child.cget("text"))
                        if text_id:
                            if text_id == "copy_clipboard_button":
                                child.config(text=self.translate("copy_clipboard_button"))
                            elif text_id == "save_file_button":
                                child.config(text=self.translate("save_file_button"))
                            elif text_id == "delete_files_button":
                                child.config(text=self.translate("delete_files_button"))

    def update_stream_tab_language(self):
        # Update labels and buttons in Stream Duplicate Checker tab
        for widget in self.tab_stream.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        text_id = self.get_text_id(child.cget("text"))
                        if text_id:
                            if text_id == "stream_root_dir_label":
                                child.config(text=self.translate("stream_root_dir_label"))
                    elif isinstance(child, ttk.Button):
                        text_id = self.get_text_id(child.cget("text"))
                        if text_id:
                            if text_id == "stream_browse_button":
                                child.config(text=self.translate("stream_browse_button"))
                            elif text_id == "stream_scan_button":
                                child.config(text=self.translate("stream_scan_button"))
                            elif text_id == "stream_select_all_button":
                                child.config(text=self.translate("stream_select_all_button"))
                            elif text_id == "stream_copy_clipboard_button":
                                child.config(text=self.translate("stream_copy_clipboard_button"))
                            elif text_id == "stream_save_file_button":
                                child.config(text=self.translate("stream_save_file_button"))
                            elif text_id == "stream_delete_duplicates_button":
                                child.config(text=self.translate("stream_delete_duplicates_button"))
        # Update Treeview headers
        self.stream_tree.heading("select", text=self.translate("stream_select_column"))
        self.stream_tree.heading("duplicate_file", text=self.translate("stream_duplicate_file_column"))
        self.stream_tree.heading("locations", text=self.translate("stream_locations_column"))

    def get_text_id(self, text):
        """
        Helper function to get the text ID based on the current language translations.
        """
        for key, translations in self.translations.items():
            if key in translations:
                for id_key, id_text in translations[key].items():
                    if id_text == text:
                        return id_key
        return None

    # ========================= YFT Cleaner Functions =========================

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
            List[str]: a list of all found '_hi.yft' files.
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

    def show_yft_context_menu(self, event):
        # Ensure a row is clicked
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.right_clicked_row = row_id  # Record the right-clicked row
            self.yft_context_menu.post(event.x_root, event.y_root)
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
            if self.tree.set(item, "select") == "☑":  # 修正條件為 "☑"
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

    # ========================= Stream Duplicate Checker Functions =========================

    def browse_stream_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.stream_root_directory.set(directory)

    def start_stream_scan(self):
        if not self.stream_root_directory.get():
            messagebox.showwarning("Warning", self.translate("stream_info_no_selected"))
            return

        if not os.path.isdir(self.stream_root_directory.get()):
            messagebox.showerror("Error", self.translate("stream_info_no_duplicates"))
            return

        # Clear Stream Treeview
        for item in self.stream_tree.get_children():
            self.stream_tree.delete(item)
        self.duplicate_files.clear()
        self.total_stream_files = 0
        self.processed_stream_files = 0
        self.stream_progress["value"] = 0
        self.stream_lbl_progress.config(text=self.translate("stream_progress_label", self.processed_stream_files, self.total_stream_files))

        # Update status
        self.status.set(self.translate("stream_status_scanning"))

        threading.Thread(target=self.scan_stream_duplicates, daemon=True).start()

    def scan_stream_duplicates(self):
        try:
            stream_files = self.find_stream_files(self.stream_root_directory.get())
            self.total_stream_files = len(stream_files)
            self.update_stream_progress()

            file_dict = {}
            for file in stream_files:
                filename = os.path.basename(file)
                if filename in file_dict:
                    file_dict[filename].append(os.path.dirname(file))
                else:
                    file_dict[filename] = [os.path.dirname(file)]
                self.processed_stream_files += 1
                self.update_stream_progress()

            # Identify duplicates
            duplicates = {k: v for k, v in file_dict.items() if len(v) > 1}
            self.duplicate_files = duplicates
            self.populate_stream_treeview(duplicates)
            if duplicates:
                self.status.set(self.translate("stream_status_completed"))
            else:
                self.status.set(self.translate("stream_info_no_duplicates"))
        except Exception as e:
            self.update_status(f"{self.translate('stream_status_error')} {e}")

    def find_stream_files(self, root_dir):
        """
        Recursively find all files within 'stream' directories.
        Args:
            root_dir (str): root directory to start the search from.

        Returns:
            List[str]: a list of all found files within 'stream' directories.
        """
        stream_files = []
        root = Path(root_dir)
        # using rglob to find all directories named 'stream'
        for stream_dir in root.rglob('stream'):
            if stream_dir.is_dir():
                for file in stream_dir.glob('**/*'):
                    if file.is_file():
                        stream_files.append(str(file))
        return stream_files

    def populate_stream_treeview(self, duplicates):
        """
        duplicates: dict where key is duplicate file name, value is list of locations
        """
        for file_name, locations in duplicates.items():
            locations_str = '; '.join(locations)
            self.stream_tree.insert(
                "",
                tk.END,
                values=("☐", file_name, locations_str),
                tags=("duplicate",)
            )
            self.stream_tree.tag_configure("duplicate", background="lightcoral")

    def select_all_stream(self):
        for item in self.stream_tree.get_children():
            self.stream_tree.set(item, "select", "☑")

    def handle_click_stream(self, event):
        region = self.stream_tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        column = self.stream_tree.identify_column(event.x)
        if column == "#1":  # 'select' column
            row_id = self.stream_tree.identify_row(event.y)
            if row_id:
                current_value = self.stream_tree.set(row_id, "select")
                new_value = "☑" if current_value == "☐" else "☐"
                self.stream_tree.set(row_id, "select", new_value)

    def show_stream_context_menu(self, event):
        # Ensure a row is clicked
        row_id = self.stream_tree.identify_row(event.y)
        if row_id:
            self.stream_tree.selection_set(row_id)
            self.right_clicked_row = row_id  # Record the right-clicked row

            # Clear previous menu items
            self.stream_context_menu.delete(0, tk.END)

            # Get the duplicate file and its locations
            duplicate_file = self.stream_tree.set(row_id, "duplicate_file")
            locations_str = self.stream_tree.set(row_id, "locations")
            locations = locations_str.split('; ')

            # 美化上下文選單：添加分隔線和改變字體樣式
            self.stream_context_menu.add_command(
                label="📂 " + self.translate("view_folder"),
                command=lambda: self.open_folder_first_location(duplicate_file, locations)
            )
            self.stream_context_menu.add_separator()

            # For each location, add a submenu item with icons and better formatting
            for loc in locations:
                self.stream_context_menu.add_command(
                    label=f"🔍 {loc}",
                    command=lambda loc=loc: self.open_folder(os.path.join(loc, duplicate_file))
                )
                self.stream_context_menu.add_command(
                    label=f"🗑️ Delete {loc}",
                    command=lambda loc=loc: self.delete_specific_duplicate(os.path.join(loc, duplicate_file))
                )

            # Add a separator before bulk actions
            self.stream_context_menu.add_separator()
            self.stream_context_menu.add_command(
                label="❌ Delete All Duplicates",
                command=lambda: self.delete_all_duplicates(duplicate_file, locations)
            )

            # Show the context menu
            self.stream_context_menu.post(event.x_root, event.y_root)
        else:
            self.right_clicked_row = None  # Reset if not clicking on a row

    def open_folder_first_location(self, duplicate_file, locations):
        if locations:
            first_location = locations[0]
            self.open_folder(os.path.join(first_location, duplicate_file))

    def open_folder(self, file_path):
        folder_path = os.path.dirname(file_path)
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

    def delete_specific_duplicate(self, file_path):
        confirm = messagebox.askyesno(
            self.translate("stream_confirm_delete_title"),
            f"{self.translate('stream_confirm_delete_message')}\n{file_path}"
        )
        if not confirm:
            return

        try:
            os.remove(file_path)
            messagebox.showinfo("Success", self.translate("stream_success_delete", 1))
            # Remove from Treeview
            for item in self.stream_tree.get_children():
                if self.stream_tree.set(item, "duplicate_file") == os.path.basename(file_path):
                    locations_str = self.stream_tree.set(item, "locations")
                    locations = locations_str.split('; ')
                    loc_dir = os.path.dirname(file_path)
                    if loc_dir in locations:
                        locations.remove(loc_dir)
                        if len(locations) <= 1:
                            # If only one or no locations remain, remove the item from the Treeview
                            self.stream_tree.delete(item)
                            # Also update the duplicate_files dictionary
                            if len(locations) == 1:
                                file_name = self.stream_tree.set(item, "duplicate_file")
                                single_loc = locations[0]
                                self.duplicate_files.pop(file_name, None)
                        else:
                            # Update the locations
                            new_locations_str = '; '.join(locations)
                            self.stream_tree.set(item, "locations", new_locations_str)
                    break
        except Exception as e:
            messagebox.showerror("Error", f"{self.translate('stream_error_delete').format(file_path)}\n{e}")

    def delete_all_duplicates(self, duplicate_file, locations):
        confirm = messagebox.askyesno(
            self.translate("stream_confirm_delete_title"),
            f"{self.translate('stream_confirm_delete_message')}\n{duplicate_file}"
        )
        if not confirm:
            return

        deleted = []
        failed = []
        for loc in locations:
            full_path = os.path.join(loc, duplicate_file)
            try:
                os.remove(full_path)
                deleted.append(full_path)
            except Exception as e:
                failed.append((full_path, str(e)))

        if deleted:
            messagebox.showinfo("Success", self.translate("stream_success_delete", len(deleted)))
            # Remove the item from Treeview since all duplicates are deleted
            for item in self.stream_tree.get_children():
                if self.stream_tree.set(item, "duplicate_file") == duplicate_file:
                    self.stream_tree.delete(item)
                    break
            # Also update the duplicate_files dictionary
            self.duplicate_files.pop(duplicate_file, None)

        if failed:
            error_msg = "\n".join([f"{p}: {err}" for p, err in failed])
            messagebox.showerror("Error", self.translate("stream_error_delete", error_msg))

        self.status.set(self.translate("stream_status_completed"))

    def copy_stream_to_clipboard(self):
        duplicates = self.duplicate_files
        if not duplicates:
            messagebox.showinfo("Info", self.translate("stream_info_no_duplicates"))
            return
        try:
            duplicate_list = []
            for file, locations in duplicates.items():
                duplicate_list.append(f"{file}:\n" + "\n".join(locations))
            pyperclip.copy('\n\n'.join(duplicate_list))
            messagebox.showinfo("Success", self.translate("stream_info_copy_success"))
        except pyperclip.PyperclipException as e:
            messagebox.showerror("Error", f"{self.translate('stream_status_error')} {e}")

    def save_stream_to_file(self):
        duplicates = self.duplicate_files
        if not duplicates:
            messagebox.showinfo("Info", self.translate("stream_info_no_duplicates"))
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title=self.translate("stream_save_file_button")
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for file, locations in duplicates.items():
                        f.write(f"{file}:\n")
                        for loc in locations:
                            f.write(f"{loc}\n")
                        f.write("\n")
                messagebox.showinfo("Success", self.translate("stream_info_save_success", file_path))
            except Exception as e:
                messagebox.showerror("Error", f"{self.translate('stream_status_error')} {e}")

    def delete_selected_stream_duplicates(self):
        selected = self.get_selected_stream_duplicates()
        if not selected:
            messagebox.showinfo("Info", self.translate("stream_info_no_selected"))
            return

        confirm = messagebox.askyesno(
            self.translate("stream_confirm_delete_title"),
            self.translate("stream_confirm_delete_message")
        )
        if not confirm:
            return

        deleted = []
        failed = []
        for file_name, locations in selected.items():
            # Keep the first occurrence, delete the rest
            for loc in locations[1:]:
                full_path = os.path.join(loc, file_name)
                try:
                    os.remove(full_path)
                    deleted.append(full_path)
                    # Remove from Treeview
                    for item in self.stream_tree.get_children():
                        if self.stream_tree.set(item, "duplicate_file") == file_name and loc in self.stream_tree.set(item, "locations"):
                            # Update the locations
                            locations_str = self.stream_tree.set(item, "locations")
                            locs = locations_str.split('; ')
                            if loc in locs:
                                locs.remove(loc)
                                if len(locs) <=1:
                                    # If only one or no locations remain, remove the item
                                    self.stream_tree.delete(item)
                                    # Also update the duplicate_files dictionary
                                    if len(locs) == 1:
                                        self.duplicate_files.pop(file_name, None)
                                else:
                                    # Update the locations
                                    new_locations_str = '; '.join(locs)
                                    self.stream_tree.set(item, "locations", new_locations_str)
                    # After deletion, check if only one location remains
                except Exception as e:
                    failed.append((full_path, str(e)))

        if deleted:
            messagebox.showinfo("Success", self.translate("stream_success_delete", len(deleted)))

        if failed:
            error_msg = "\n".join([f"{p}: {err}" for p, err in failed])
            messagebox.showerror("Error", self.translate("stream_error_delete", error_msg))

        # Refresh duplicate_files dictionary
        self.refresh_duplicate_files()

        self.status.set(self.translate("stream_status_completed"))

    def get_selected_stream_duplicates(self):
        selected_duplicates = {}
        for item in self.stream_tree.get_children():
            if self.stream_tree.set(item, "select") == "☑":
                file_name = self.stream_tree.set(item, "duplicate_file")
                locations_str = self.stream_tree.set(item, "locations")
                locations = locations_str.split('; ')
                selected_duplicates[file_name] = locations
        return selected_duplicates

    def refresh_duplicate_files(self):
        # Re-scan the treeview to rebuild the duplicate_files dictionary
        duplicates = {}
        for item in self.stream_tree.get_children():
            file_name = self.stream_tree.set(item, "duplicate_file")
            locations_str = self.stream_tree.set(item, "locations")
            locations = locations_str.split('; ')
            duplicates[file_name] = locations
        self.duplicate_files = duplicates

    def update_stream_progress(self):
        if self.total_stream_files > 0:
            progress_percent = (self.processed_stream_files / self.total_stream_files) * 100
            self.stream_progress["value"] = progress_percent
            self.stream_lbl_progress.config(text=self.translate("stream_progress_label", self.processed_stream_files, self.total_stream_files))
            self.root.update_idletasks()

    # ========================= Common Functions =========================

    # Note: copy_stream_to_clipboard and save_stream_to_file are already defined above,
    # so ensure there are no duplicate definitions.

    # ========================= Main Function =========================

    def main():
        root = tk.Tk()
        app = HiYftGuiTool(root)
        root.mainloop()


if __name__ == "__main__":
    HiYftGuiTool.main()
