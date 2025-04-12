import os
import struct
import hashlib
import pyperclip
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# -----------------------------------#
# 1. Multi-Language Translation (Translator)
# -----------------------------------#
class Translator:
    """
    Translation management class.
    Responsible for maintaining dictionaries for various languages,
    providing an external translate(...) method to get the corresponding text.
    
    alias: Translator
    parameter: language_code (str) - default is "en"
    """
    def __init__(self, language_code="en"):
        self.current_language = language_code

        # You can place all translation dictionaries here
        self.translations = {
            "en": {
                "title": "Duplicate YFT Cleaner",
                "root_dir_label": "Root Directory:",
                "browse_button": "Browse...",
                "scan_button": "Start Scan",
                "progress_label": "Progress: {}/{}",
                "select_all_button": "Select All",
                "select_column": "Select",
                "model_name_column": "Model Name",
                "path_column": "File Path",
                "size_column": "Size (MB)",
                "status_column": "Oversize?",
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
                "status_oversize": "Critical Oversized",
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
                "manual_check_button": "Manual Check for Duplicates",
                "stream_info_no_selected": "No directory selected.",
                "stream_info_no_files": "No directory or invalid path selected.",
                "stream_status_scanning": "Scanning...",
                "stream_status_completed": "Scan Completed.",
                "stream_status_error": "Error:",
                "manual_check_results": "Manual Check Results:",
                "not_found": "NOT FOUND",
                "duplicates_label": "Duplicate(s) Found in:",
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
                "status_oversize": "過大",
                "oversized_warning": "Oversized assets can and WILL lead to streaming issues (例如模型未載入/渲染)。",
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
                # Manual Duplicate Check texts
                "manual_check_button": "手動重複檢查",
                "stream_info_no_selected": "未選擇任何資料夾。",
                "stream_info_no_files": "沒有可用的資料夾，或路徑無效。",
                "stream_status_scanning": "掃描中...",
                "stream_status_completed": "掃描完成。",
                "stream_status_error": "錯誤：",
                "manual_check_results": "手動重複檢查結果：",
                "not_found": "未發現檔案",
                "duplicates_label": "重複檔案位置：",
            },
            # 可依需求增加其他語系
        }

    def set_language(self, language_code: str):
        """
        Set the current language.
        
        alias: set_language
        parameter: language_code (str)
        """
        self.current_language = language_code

    def translate(self, text_id: str, *args) -> str:
        """
        Return the text corresponding to the current language.
        If text_id does not exist in the dictionary, return text_id directly.
        If formatting is needed (e.g., "Progress: {}/{}"), pass the args accordingly.
        
        alias: translate
        parameter: text_id (str)
        parameter: *args
        """
        lang_map = self.translations.get(self.current_language, {})
        text = lang_map.get(text_id, text_id)
        if args:
            return text.format(*args)
        return text

# -------------------------#
# 2. YFT Cleaner Logic
# -------------------------#
class YftCleaner:
    """
    A class dedicated to handling YFT ( *_hi.yft ) file scanning, size and status checking, deletion, etc.
    
    alias: YftCleaner
    parameter: translator (Translator)
    parameter: size_margin_kb (float) - the allowed difference in KB for considering two files 'identical' if their hashes differ
    """
    def __init__(self, translator: Translator, size_margin_kb: float = 0.0):
        self._tr = translator
        self.deletable_files = []
        self.size_margin_kb = size_margin_kb

    def find_hi_yft_files(self, root_dir: str):
        """
        Recursively find all `*_hi.yft` files in any 'stream' folder under root_dir.
        Return: List of file paths (List[str])

        alias: find_hi_yft_files
        parameter: root_dir (str)
        """
        hi_yft_files = []
        root = Path(root_dir)
        for stream_dir in root.rglob('stream'):
            if stream_dir.is_dir():
                for yft_file in stream_dir.glob('**/*_hi.yft'):
                    hi_yft_files.append(str(yft_file))
        return hi_yft_files

    def scan_files(self, root_directory: str):
        """
        Main entry point for performing the scanning procedure.
        Return: List of tuples: [(file_path, size_str, status), ...]

        alias: scan_files
        parameter: root_directory (str)
        """
        hi_yft_files = self.find_hi_yft_files(root_directory)
        unique_hi_yft_files = list(set(hi_yft_files))
        results = []

        for f in unique_hi_yft_files:
            item = self.process_file(f)
            if item:
                results.append(item)
        self.deletable_files = results
        return results

    def process_file(self, hi_file: str):
        """
        Performs logic for a given hi_file, including:
          1. Try to match with the original file (model.yft)
          2. Compare hashes
          3. If hash mismatch, optionally check if size difference is within margin_kb
          4. If considered identical, read header, check RSC7/8, compute size, determine status, etc.

        Return: (file_path, size_str, status) or None

        alias: process_file
        parameter: hi_file (str)
        """
        original_file = self.get_original_file(hi_file)
        if not original_file or not os.path.isfile(original_file):
            return None

        # Step 1) Compute hashes
        hi_hash = self.compute_file_hash(hi_file)
        org_hash = self.compute_file_hash(original_file)

        # We'll track difference in bytes if we use margin
        diff_bytes = 0
        used_margin = False

        # Step 2) If hashes match, consider them identical
        if hi_hash and org_hash and hi_hash == org_hash:
            return self._process_identical_files(hi_file, diff_bytes=0)

        # Step 3) If hashes mismatch, check if size difference is within user margin
        if self.size_margin_kb > 0.0:
            size_hi_bytes = os.path.getsize(hi_file)
            size_org_bytes = os.path.getsize(original_file)
            diff_bytes = abs(size_hi_bytes - size_org_bytes)
            diff_kb = diff_bytes / 1024.0

            if diff_kb <= self.size_margin_kb:
                used_margin = True
                return self._process_identical_files(hi_file, diff_bytes=diff_bytes)

        # If neither matched nor within margin => not identical
        return None

    def _process_identical_files(self, hi_file: str, diff_bytes: int):
        """
        Helper method to handle the rest of the logic if hi_file is considered identical to its original.
        Reads the header, checks resource type, calculates size/status, etc.

        alias: _process_identical_files
        parameter: hi_file (str)
        parameter: diff_bytes (int) - difference in bytes if margin is used, otherwise 0
        """
        # Read header
        is_resource, physPages, virtPages = self.read_yft_header(hi_file)

        if is_resource:
            phys_size = self.convert_rsc7_size(physPages)
            virt_size = self.convert_rsc7_size(virtPages)
            phys_mb = phys_size / (1024.0 * 1024.0)
            virt_mb = virt_size / (1024.0 * 1024.0)
            size_str = f"PH:{phys_mb:.2f}/VR:{virt_mb:.2f} MB"
            max_mb = max(phys_mb, virt_mb)
            status = self.determine_status(max_mb)
            if status == self._tr.translate("status_oversize"):
                pass
            elif status in [self._tr.translate("status_warning"), self._tr.translate("status_critical")]:
                status += f" - {self._tr.translate('oversized_warning')}"
            else:
                status += " - good"
        else:
            # Not a recognized RSC resource, fall back to actual file size
            actual_size = os.path.getsize(hi_file)
            actual_mb = actual_size / (1024.0 * 1024.0)
            size_str = f"{actual_mb:.2f} MB"
            status = self.determine_status(actual_mb)
            if status == self._tr.translate("status_oversize"):
                pass
            elif status in [self._tr.translate("status_warning"), self._tr.translate("status_critical")]:
                status += f" - {self._tr.translate('oversized_warning')}"
            else:
                status += " - Unknown format"

        # If diff_bytes > 0, append margin info to the status
        if diff_bytes > 0:
            status += f" [Margin used: diff={diff_bytes} bytes]"

        return (hi_file, size_str, status)

    def get_original_file(self, hi_file: str):
        """
        Retrieve the original file corresponding to hi_file (replace '_hi' with '').
        Return: path to the original file or None if not found.

        alias: get_original_file
        parameter: hi_file (str)
        """
        dirpath, hi_filename = os.path.split(hi_file)
        base_name, ext = os.path.splitext(hi_filename)
        if '_hi' not in base_name.lower():
            return None
        original_base_name = base_name.lower().replace('_hi', '')
        original_filename = original_base_name + ext
        return os.path.join(dirpath, original_filename)

    def compute_file_hash(self, file_path: str):
        """
        Compute the SHA256 hash of a file.
        Return: Hexadecimal digest string or None if error.

        alias: compute_file_hash
        parameter: file_path (str)
        """
        try:
            hash_func = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            print(f"{self._tr.translate('status_error')} {e}")
            return None

    def read_yft_header(self, file_path: str):
        """
        Read the YFT file header.
        Return: (is_resource, rscPagesPhysical, rscPagesVirtual)

        alias: read_yft_header
        parameter: file_path (str)
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
                if len(header) < 16:
                    return (False, 0, 0)
                magic, version, virtPages, physPages = struct.unpack('<IIII', header)
                if magic in [0x37435352, 0x38435352]:
                    return (True, physPages, virtPages)
                elif magic == 0x05435352:
                    return (True, version, virtPages)
                else:
                    return (False, 0, 0)
        except Exception as e:
            print(f"{self._tr.translate('status_error')} {e}")
            return (False, 0, 0)

    def convert_rsc7_size(self, flags: int):
        """
        Reference: C++ ConvertRSC7Size.
        Convert flags to size in bytes.

        alias: convert_rsc7_size
        parameter: flags (int)
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

    def determine_status(self, size_mb: float):
        """
        Determine the status based on size in MB.

        alias: determine_status
        parameter: size_mb (float)
        """
        if size_mb > 64:
            return self._tr.translate("status_oversize")
        elif size_mb > 32:
            return self._tr.translate("status_critical")
        elif size_mb > 16:
            return self._tr.translate("status_warning")
        else:
            return self._tr.translate("status_ok")


# ------------------------------------------#
# 3. Stream Duplicate Checker Logic
# ------------------------------------------#
class StreamDuplicateChecker:
    """
    A class dedicated to scanning and removing duplicate files in 'Stream' folders
    (based on filenames).
    
    alias: StreamDuplicateChecker
    parameter: translator (Translator)
    """
    def __init__(self, translator: Translator):
        self._tr = translator
        self.duplicate_files = {}

    def scan_stream_duplicates(self, stream_root_directory: str):
        """
        Scan 'stream_root_directory' for all 'stream' folders and gather all files.
        Then determine duplicates based on filename alone.
        Return: dictionary of duplicates.

        alias: scan_stream_duplicates
        parameter: stream_root_directory (str)
        """
        stream_files = self.find_stream_files(stream_root_directory)
        file_dict = {}
        for file in stream_files:
            filename = os.path.basename(file)
            if filename not in file_dict:
                file_dict[filename] = [os.path.dirname(file)]
            else:
                file_dict[filename].append(os.path.dirname(file))

        duplicates = {k: v for k, v in file_dict.items() if len(v) > 1}
        self.duplicate_files = duplicates
        return duplicates

    def find_stream_files(self, root_dir: str):
        """
        Recursively find all files in any 'stream' folders under root_dir.
        Return: List of file paths.

        alias: find_stream_files
        parameter: root_dir (str)
        """
        stream_files = []
        root = Path(root_dir)
        for stream_dir in root.rglob('stream'):
            if stream_dir.is_dir():
                for file in stream_dir.glob('**/*'):
                    if file.is_file():
                        stream_files.append(str(file))
        return stream_files

# ----------------------------------------#
# 4. GUI and Main Controller
# ----------------------------------------#
class GUI_MAIN:
    """
    A class responsible for managing the entire Tkinter GUI,
    combining YftCleaner and StreamDuplicateChecker objects 
    and handling user interactions.
    
    alias: GUI_MAIN
    parameter: root (Tk)
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Stream files assistant by pgonintwitch")
        self.root.geometry("1150x800")
        self.root.resizable(True, True)

        # Default language
        self.translator = Translator(language_code="en")
        self.current_language = "en"

        # Margin-related variables (checkbox + entry for KB)
        self.enable_margin_var = tk.BooleanVar(value=False)     # Whether margin is enabled
        self.size_margin_kb_var = tk.StringVar(value="0.0")     # Margin in KB as string

        # Will be created after user hits 'Start Scan'
        self.yft_cleaner = None
        self.stream_checker = None

        self.root_directory = tk.StringVar()
        self.stream_root_directory = tk.StringVar()
        self.total_files = 0
        self.processed_files = 0
        self.total_stream_files = 0
        self.processed_stream_files = 0
        self.sort_column = None
        self.sort_reverse = False
        self.right_clicked_row = None

        # Build UI
        self.setup_ui()

    # ------------------------------#
    # Helper & Translation
    # ------------------------------#
    def translate(self, text_id, *args):
        """
        Shortcut to use the translator object.
        
        alias: translate
        parameter: text_id (str)
        parameter: *args
        """
        return self.translator.translate(text_id, *args)

    def set_language(self, lang_code: str):
        """
        Set the current language and update translator.
        
        alias: set_language
        parameter: lang_code (str)
        """
        self.current_language = lang_code
        self.translator.set_language(lang_code)

    # ------------------------------#
    # UI Setup
    # ------------------------------#
    def setup_ui(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Calibri', 12, 'bold'))
        style.configure("TButton", padding=6, font=('Calibri', 10))
        style.configure("TLabel", font=('Calibri', 10))
        style.configure("TCombobox", font=('Calibri', 10))

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: YFT Cleaner
        self.tab_yft = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_yft, text=self.translate("title"))
        self.setup_yft_tab()

        # Tab 2: Stream Duplicate Checker
        self.tab_stream = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_stream, text=self.translate("stream_tab"))
        self.setup_stream_tab()

        # Status bar
        self.status = tk.StringVar()
        self.status.set(self.translate("status_ready"))
        lbl_status = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor="w")
        lbl_status.pack(fill=tk.X, side=tk.BOTTOM)

        # Right-click menus
        self.yft_context_menu = tk.Menu(self.root, tearoff=0)
        self.yft_context_menu.add_command(label=self.translate("view_folder"), command=self.view_folder)

        self.stream_context_menu = tk.Menu(self.root, tearoff=0)

    def setup_yft_tab(self):
        frame_top = ttk.Frame(self.tab_yft, padding=10)
        frame_top.pack(fill=tk.X)

        lbl_dir = ttk.Label(frame_top, text=self.translate("root_dir_label"))
        lbl_dir.grid(row=0, column=0, sticky="w", padx=(0, 5))

        entry_dir = ttk.Entry(frame_top, textvariable=self.root_directory, width=60)
        entry_dir.grid(row=0, column=1, sticky="w", padx=(0, 5))

        btn_browse = ttk.Button(frame_top, text=self.translate("browse_button"), command=self.browse_directory)
        btn_browse.grid(row=0, column=2, sticky="w")

        # Language switch
        lbl_language = ttk.Label(frame_top, text=self.translate("language_label"))
        lbl_language.grid(row=0, column=3, sticky="w", padx=(20, 5))

        self.language_var = tk.StringVar(value="en")
        cmb_language = ttk.Combobox(
            frame_top, textvariable=self.language_var, state="readonly",
            values=list(self.translator.translations.keys()), width=10
        )
        cmb_language.grid(row=0, column=4, sticky="w")
        cmb_language.bind("<<ComboboxSelected>>", self.change_language)

        # ------------------------------
        # Margin UI
        # ------------------------------
        frame_margin = ttk.Frame(self.tab_yft, padding=(0, 5))
        frame_margin.pack(fill=tk.X)

        check_margin = ttk.Checkbutton(
            frame_margin,
            text="Enable size margin (KB)",
            variable=self.enable_margin_var
        )
        check_margin.grid(row=0, column=0, sticky="w")

        entry_margin_kb = ttk.Entry(frame_margin, textvariable=self.size_margin_kb_var, width=10)
        entry_margin_kb.grid(row=0, column=1, padx=(5, 0), sticky="w")
        # ------------------------------

        frame_scan = ttk.Frame(self.tab_yft, padding=10)
        frame_scan.pack(fill=tk.X)

        btn_scan = ttk.Button(frame_scan, text=self.translate("scan_button"), command=self.start_scan)
        btn_scan.grid(row=0, column=0, sticky="w")

        self.progress = ttk.Progressbar(frame_scan, orient="horizontal", length=500, mode="determinate")
        self.progress.grid(row=0, column=1, padx=10, sticky="w")

        self.lbl_progress = ttk.Label(frame_scan, text=self.translate("progress_label", 0, 0))
        self.lbl_progress.grid(row=0, column=2, sticky="w")

        frame_select_all = ttk.Frame(self.tab_yft, padding=(10, 0))
        frame_select_all.pack(fill=tk.X)
        btn_select_all = ttk.Button(frame_select_all, text=self.translate("select_all_button"), command=self.select_all_yft)
        btn_select_all.pack(anchor='w')

        frame_list = ttk.Frame(self.tab_yft, padding=10)
        frame_list.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for YFT list
        scrollbar_yft = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
        scrollbar_yft.pack(side=tk.RIGHT, fill=tk.Y)

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

        self.tree.configure(yscrollcommand=scrollbar_yft.set)
        scrollbar_yft.config(command=self.tree.yview)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind('<Button-1>', self.handle_click_yft)
        self.tree.bind('<Button-3>', self.show_yft_context_menu)

        frame_actions = ttk.Frame(self.tab_yft, padding=10)
        frame_actions.pack(fill=tk.X)
        btn_copy = ttk.Button(frame_actions, text=self.translate("copy_clipboard_button"), command=self.copy_to_clipboard_yft)
        btn_copy.pack(side=tk.LEFT, padx=5)
        btn_save = ttk.Button(frame_actions, text=self.translate("save_file_button"), command=self.save_to_file_yft)
        btn_save.pack(side=tk.LEFT, padx=5)
        btn_delete = ttk.Button(frame_actions, text=self.translate("delete_files_button"), command=self.delete_selected_files_yft)
        btn_delete.pack(side=tk.LEFT, padx=5)

    def setup_stream_tab(self):
        frame_top = ttk.Frame(self.tab_stream, padding=10)
        frame_top.pack(fill=tk.X)

        lbl_dir = ttk.Label(frame_top, text=self.translate("stream_root_dir_label"))
        lbl_dir.grid(row=0, column=0, sticky="w", padx=(0, 5))

        entry_dir = ttk.Entry(frame_top, textvariable=self.stream_root_directory, width=60)
        entry_dir.grid(row=0, column=1, sticky="w", padx=(0, 5))

        btn_browse = ttk.Button(frame_top, text=self.translate("stream_browse_button"), command=self.browse_stream_directory)
        btn_browse.grid(row=0, column=2, sticky="w")

        frame_scan = ttk.Frame(self.tab_stream, padding=10)
        frame_scan.pack(fill=tk.X)

        btn_scan = ttk.Button(frame_scan, text=self.translate("stream_scan_button"), command=self.start_stream_scan)
        btn_scan.grid(row=0, column=0, sticky="w")

        self.stream_progress = ttk.Progressbar(frame_scan, orient="horizontal", length=500, mode="determinate")
        self.stream_progress.grid(row=0, column=1, padx=10, sticky="w")

        self.stream_lbl_progress = ttk.Label(frame_scan, text=self.translate("stream_progress_label", 0, 0))
        self.stream_lbl_progress.grid(row=0, column=2, sticky="w")

        frame_select_all = ttk.Frame(self.tab_stream, padding=(10, 0))
        frame_select_all.pack(fill=tk.X)
        btn_select_all_stream = ttk.Button(frame_select_all, text=self.translate("stream_select_all_button"), command=self.select_all_stream)
        btn_select_all_stream.pack(anchor='w')

        frame_list = ttk.Frame(self.tab_stream, padding=10)
        frame_list.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for stream list
        scrollbar_stream = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
        scrollbar_stream.pack(side=tk.RIGHT, fill=tk.Y)

        stream_columns = ("select", "duplicate_file", "locations")
        self.stream_tree = ttk.Treeview(frame_list, columns=stream_columns, show="headings", selectmode="none")
        self.stream_tree.heading("select", text=self.translate("stream_select_column"), command=lambda: self.sort_stream_tree("select"))
        self.stream_tree.heading("duplicate_file", text=self.translate("stream_duplicate_file_column"), command=lambda: self.sort_stream_tree("duplicate_file"))
        self.stream_tree.heading("locations", text=self.translate("stream_locations_column"), command=lambda: self.sort_stream_tree("locations"))

        self.stream_tree.column("select", width=80, anchor="center")
        self.stream_tree.column("duplicate_file", width=300, anchor="w")
        self.stream_tree.column("locations", width=700, anchor="w")

        self.stream_tree.configure(yscrollcommand=scrollbar_stream.set)
        scrollbar_stream.config(command=self.stream_tree.yview)

        self.stream_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.stream_tree.bind('<Button-1>', self.handle_click_stream)
        self.stream_tree.bind('<Button-3>', self.show_stream_context_menu)

        frame_actions = ttk.Frame(self.tab_stream, padding=10)
        frame_actions.pack(fill=tk.X)
        btn_copy = ttk.Button(frame_actions, text=self.translate("stream_copy_clipboard_button"), command=self.copy_stream_to_clipboard)
        btn_copy.pack(side=tk.LEFT, padx=5)
        btn_save = ttk.Button(frame_actions, text=self.translate("stream_save_file_button"), command=self.save_stream_to_file)
        btn_save.pack(side=tk.LEFT, padx=5)

        frame_manual = ttk.Frame(self.tab_stream, padding=10)
        frame_manual.pack(fill=tk.BOTH, expand=True)

        btn_manual_check = ttk.Button(frame_manual, text=self.translate("manual_check_button"), command=self.check_manual_duplicates)
        btn_manual_check.pack(anchor="e", pady=5)

        self.txt_manual = tk.Text(frame_manual, height=10)
        self.txt_manual.pack(fill=tk.BOTH, expand=True)

    # --------------------------------------#
    # YFT Cleaner Events
    # --------------------------------------#
    def browse_directory(self):
        """
        Browse for a directory to set the YFT root path.
        
        alias: browse_directory
        """
        directory = filedialog.askdirectory()
        if directory:
            self.root_directory.set(directory)

    def start_scan(self):
        """
        Start scanning for *_hi.yft files.
        
        alias: start_scan
        """
        if self.enable_margin_var.get():
            try:
                margin_kb = float(self.size_margin_kb_var.get())
            except ValueError:
                margin_kb = 0.0
        else:
            margin_kb = 0.0

        self.yft_cleaner = YftCleaner(self.translator, size_margin_kb=margin_kb)

        if not self.root_directory.get():
            messagebox.showwarning("Warning", self.translate("info_no_selected"))
            return
        if not os.path.isdir(self.root_directory.get()):
            messagebox.showerror("Error", self.translate("info_no_files"))
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.yft_cleaner.deletable_files.clear()
        self.total_files = 0
        self.processed_files = 0
        self.progress["value"] = 0
        self.lbl_progress.config(text=self.translate("progress_label", 0, 0))
        self.status.set(self.translate("status_scanning"))

        threading.Thread(target=self.scan_files_thread, daemon=True).start()

    def scan_files_thread(self):
        """
        Worker thread to scan files in the background.
        
        alias: scan_files_thread
        """
        try:
            hi_yft_files = self.yft_cleaner.find_hi_yft_files(self.root_directory.get())
            unique_hi_yft_files = list(set(hi_yft_files))
            self.total_files = len(unique_hi_yft_files)

            results = []
            with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
                future_map = {executor.submit(self.yft_cleaner.process_file, f): f for f in unique_hi_yft_files}
                for idx, future in enumerate(as_completed(future_map), 1):
                    r = future.result()
                    if r:
                        results.append(r)
                    self.processed_files = idx
                    self.update_progress()

            self.yft_cleaner.deletable_files = results
            self.populate_treeview_yft(results)
            self.status.set(self.translate("status_completed"))
        except Exception as e:
            self.status.set(f"{self.translate('status_error')} {e}")

    def update_progress(self):
        """
        Update the progress bar and label for YFT scanning.
        
        alias: update_progress
        """
        if self.total_files > 0:
            progress_percent = (self.processed_files / self.total_files) * 100
            self.progress["value"] = progress_percent
            self.lbl_progress.config(text=self.translate("progress_label", self.processed_files, self.total_files))
        self.root.update_idletasks()

    def populate_treeview_yft(self, file_info_list):
        """
        Populate the YFT TreeView with the scanned file information.
        
        alias: populate_treeview_yft
        parameter: file_info_list (List[Tuple])
        """
        root_dir = self.root_directory.get()
        for file_path, size_str, status in file_info_list:
            model_name = os.path.basename(file_path)
            dir_path = os.path.dirname(file_path)
            try:
                relative_path = os.path.relpath(dir_path, root_dir)
            except ValueError:
                relative_path = dir_path

            item_id = self.tree.insert("", tk.END, values=("☐", model_name, relative_path, size_str, status))
            if status.startswith(self.translate("status_ok")):
                self.tree.item(item_id, tags=("ok",))
                self.tree.tag_configure("ok", background="lightgreen")
            elif status.startswith(self.translate("status_warning")):
                self.tree.item(item_id, tags=("warning",))
                self.tree.tag_configure("warning", background="yellow")
            elif status.startswith(self.translate("status_critical")):
                self.tree.item(item_id, tags=("critical",))
                self.tree.tag_configure("critical", background="red")
            elif status.startswith(self.translate("status_oversize")):
                self.tree.item(item_id, tags=("oversize",))
                self.tree.tag_configure("oversize", background="orange")
            else:
                self.tree.tag_configure("default", background="white")
                self.tree.item(item_id, tags=("default",))

    def handle_click_yft(self, event):
        """
        處理 YFT TreeView 點選事件，用於切換選取框 (checkbox) 狀態。
        
        alias: handle_click_yft
        parameter: event (Event)
        """
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        column = self.tree.identify_column(event.x)
        if column == "#1":
            row_id = self.tree.identify_row(event.y)
            if row_id:
                current_value = self.tree.set(row_id, "select")
                new_value = "☑" if current_value == "☐" else "☐"
                self.tree.set(row_id, "select", new_value)

    def show_yft_context_menu(self, event):
        """
        顯示 YFT 項目的右鍵選單。
        
        alias: show_yft_context_menu
        parameter: event (Event)
        """
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.right_clicked_row = row_id
            self.yft_context_menu.post(event.x_root, event.y_root)
        else:
            self.right_clicked_row = None

    def view_folder(self):
        """
        在系統檔案總管中打開所選項目的資料夾。
        
        alias: view_folder
        """
        if self.right_clicked_row:
            path_val = self.tree.set(self.right_clicked_row, "path")
            model_name = self.tree.set(self.right_clicked_row, "model_name")
            full_path = os.path.join(self.root_directory.get(), path_val, model_name)
            folder_path = os.path.dirname(full_path)
        else:
            selected = self.get_selected_files_yft()
            if not selected:
                messagebox.showinfo("Info", self.translate("info_no_selected"))
                return
            folder_path = os.path.dirname(selected[0])

        try:
            if os.name == 'nt':
                os.startfile(folder_path)
            else:
                messagebox.showerror("Error", "Unsupported OS.")
        except Exception as e:
            messagebox.showerror("Error", f"{self.translate('status_error')} {e}")

    def get_selected_files_yft(self):
        """
        取得 YFT TreeView 中被選取 (☑) 的檔案列表。
        
        alias: get_selected_files_yft
        """
        selected_files = []
        for item in self.tree.get_children():
            if self.tree.set(item, "select") == "☐":
                continue
            model_name = self.tree.set(item, "model_name")
            path_val = self.tree.set(item, "path")
            full_path = os.path.join(self.root_directory.get(), path_val, model_name)
            selected_files.append(full_path)
        return selected_files

    def copy_to_clipboard_yft(self):
        """
        將選中的 YFT 檔案路徑複製到剪貼簿。
        
        alias: copy_to_clipboard_yft
        """
        selected = self.get_selected_files_yft()
        if not selected:
            messagebox.showinfo("Info", self.translate("info_no_selected"))
            return
        try:
            pyperclip.copy('\n'.join(selected))
            messagebox.showinfo("Success", self.translate("info_copy_success"))
        except pyperclip.PyperclipException as e:
            messagebox.showerror("Error", f"{self.translate('status_error')} {e}")

    def save_to_file_yft(self):
        """
        將選中的 YFT 檔案路徑儲存到文字檔。
        
        alias: save_to_file_yft
        """
        selected = self.get_selected_files_yft()
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

    def delete_selected_files_yft(self):
        """
        刪除 YFT TreeView 中選取的檔案 (對磁碟進行刪除)。
        
        alias: delete_selected_files_yft
        """
        selected_files = self.get_selected_files_yft()
        if not selected_files:
            messagebox.showinfo("Info", self.translate("info_no_selected"))
            return

        confirm = messagebox.askyesno(self.translate("confirm_delete_title"), self.translate("confirm_delete_message", len(selected_files)))
        if not confirm:
            return

        deleted = []
        failed = []
        for fp in selected_files:
            try:
                os.remove(fp)
                deleted.append(fp)
                for item in self.tree.get_children():
                    model_name = self.tree.set(item, "model_name")
                    path_val = self.tree.set(item, "path")
                    full_check = os.path.join(self.root_directory.get(), path_val, model_name)
                    if full_check == fp:
                        self.tree.delete(item)
                        break
            except Exception as e:
                failed.append((fp, str(e)))

        if deleted:
            messagebox.showinfo("Success", self.translate("success_delete", len(deleted)))
            self.yft_cleaner.deletable_files = [df for df in self.yft_cleaner.deletable_files if df[0] not in deleted]

        if failed:
            err_msg = "\n".join([f"{p}: {msg}" for p, msg in failed])
            messagebox.showerror("Error", self.translate("error_delete", err_msg))

        self.status.set(self.translate("status_completed"))

    def select_all_yft(self):
        """
        將 YFT TreeView 中所有項目選取 (☑)。
        
        alias: select_all_yft
        """
        for item in self.tree.get_children():
            self.tree.set(item, "select", "☑")

    def sort_tree(self, column):
        """
        根據指定欄位排序 YFT TreeView。
        
        alias: sort_tree
        parameter: column (str)
        """
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_column = column

        def sort_key(item_id):
            value = self.tree.set(item_id, column)
            if column == "size":
                try:
                    if '/' in value:
                        parts = value.split('/')
                        return max(float(parts[0].split(':')[1]), float(parts[1].split(':')[1]))
                    else:
                        return float(value.split(' ')[0])
                except:
                    return 0.0
            return value.lower()

        sorted_items = sorted(self.tree.get_children(), key=sort_key, reverse=self.sort_reverse)
        for idx, item_id in enumerate(sorted_items):
            self.tree.move(item_id, '', idx)

    # ------------------------------------#
    # Stream Duplicate Checker Events
    # ------------------------------------#
    def browse_stream_directory(self):
        """
        瀏覽設定 Stream 根目錄。
        
        alias: browse_stream_directory
        """
        directory = filedialog.askdirectory()
        if directory:
            self.stream_root_directory.set(directory)

    def start_stream_scan(self):
        """
        開始掃描 'stream' 資料夾中重複的檔案。
        
        alias: start_stream_scan
        """
        if not self.stream_root_directory.get():
            messagebox.showwarning("Warning", self.translate("stream_info_no_selected"))
            return
        if not os.path.isdir(self.stream_root_directory.get()):
            messagebox.showerror("Error", self.translate("stream_info_no_duplicates"))
            return

        for item in self.stream_tree.get_children():
            self.stream_tree.delete(item)
        if not self.stream_checker:
            self.stream_checker = StreamDuplicateChecker(self.translator)

        self.stream_checker.duplicate_files.clear()
        self.total_stream_files = 0
        self.processed_stream_files = 0
        self.stream_progress["value"] = 0
        self.stream_lbl_progress.config(text=self.translate("stream_progress_label", 0, 0))
        self.status.set(self.translate("stream_status_scanning"))

        threading.Thread(target=self.scan_stream_thread, daemon=True).start()

    def scan_stream_thread(self):
        """
        掃描 Stream 資料夾重複檔案的背景執行緒。
        
        alias: scan_stream_thread
        """
        try:
            all_files = self.stream_checker.find_stream_files(self.stream_root_directory.get())
            self.total_stream_files = len(all_files)
            duplicates = self.stream_checker.scan_stream_duplicates(self.stream_root_directory.get())
            self.processed_stream_files = self.total_stream_files
            self.update_stream_progress()
            if duplicates:
                self.populate_stream_treeview(duplicates)
                self.status.set(self.translate("stream_status_completed"))
            else:
                self.status.set(self.translate("stream_info_no_duplicates"))
        except Exception as e:
            self.status.set(f"{self.translate('stream_status_error')} {e}")

    def update_stream_progress(self):
        """
        更新 Stream 掃描的進度條與進度文字。
        
        alias: update_stream_progress
        """
        if self.total_stream_files > 0:
            p = (self.processed_stream_files / self.total_stream_files) * 100
            self.stream_progress["value"] = p
            self.stream_lbl_progress.config(text=self.translate("stream_progress_label", self.processed_stream_files, self.total_stream_files))
        self.root.update_idletasks()

    def populate_stream_treeview(self, duplicates):
        """
        將重複檔案資訊填入 Stream TreeView。
        
        alias: populate_stream_treeview
        parameter: duplicates (dict)
        """
        stream_root = self.stream_root_directory.get()
        for file_name, locations in duplicates.items():
            relative_locations = []
            for loc in locations:
                try:
                    rel_loc = os.path.relpath(loc, stream_root)
                except ValueError:
                    rel_loc = loc
                relative_locations.append(rel_loc)
            loc_str = '; '.join(relative_locations)
            item_id = self.stream_tree.insert("", tk.END, values=("☐", file_name, loc_str))
            self.stream_tree.tag_configure("duplicate", background="lightcoral")
            self.stream_tree.item(item_id, tags=("duplicate",))

    def handle_click_stream(self, event):
        """
        處理 Stream TreeView 點選事件，切換選取框狀態。
        
        alias: handle_click_stream
        parameter: event (Event)
        """
        region = self.stream_tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        column = self.stream_tree.identify_column(event.x)
        if column == "#1":
            row_id = self.stream_tree.identify_row(event.y)
            if row_id:
                current_value = self.stream_tree.set(row_id, "select")
                new_value = "☑" if current_value == "☐" else "☐"
                self.stream_tree.set(row_id, "select", new_value)

    def show_stream_context_menu(self, event):
        """
        顯示 Stream 項目的右鍵選單。
        
        alias: show_stream_context_menu
        parameter: event (Event)
        """
        row_id = self.stream_tree.identify_row(event.y)
        if row_id:
            self.stream_tree.selection_set(row_id)
            self.right_clicked_row = row_id
            self.stream_context_menu.delete(0, tk.END)
            duplicate_file = self.stream_tree.set(row_id, "duplicate_file")
            locations_str = self.stream_tree.set(row_id, "locations")
            locations = locations_str.split('; ')
            self.stream_context_menu.add_command(
                label="📂 " + self.translate("view_folder"),
                command=lambda: self.open_folder_for_stream(duplicate_file, locations[0] if locations else "")
            )
            self.stream_context_menu.add_separator()
            for loc in locations:
                full_path = os.path.join(self.stream_root_directory.get(), loc, duplicate_file)
                self.stream_context_menu.add_command(
                    label=f"🔍 {loc}",
                    command=lambda path=full_path: self.open_folder_for_stream_file(path)
                )
                self.stream_context_menu.add_command(
                    label=f"🗑️ Delete {loc}",
                    command=lambda path=full_path: self.delete_stream_file(path)
                )
            self.stream_context_menu.add_separator()
            self.stream_context_menu.add_command(
                label="❌ Delete All Duplicates",
                command=lambda: self.delete_all_stream_duplicates(duplicate_file, locations)
            )
            self.stream_context_menu.post(event.x_root, event.y_root)
        else:
            self.right_clicked_row = None

    def open_folder_for_stream(self, duplicate_file, loc):
        """
        開啟指定 stream 檔案所在的資料夾。
        
        alias: open_folder_for_stream
        parameter: duplicate_file (str)
        parameter: loc (str)
        """
        path = os.path.join(self.stream_root_directory.get(), loc, duplicate_file)
        self.open_folder_for_stream_file(path)

    def open_folder_for_stream_file(self, file_path):
        """
        在系統檔案總管中開啟所給檔案所在的資料夾。
        
        alias: open_folder_for_stream_file
        parameter: file_path (str)
        """
        folder_path = os.path.dirname(file_path)
        try:
            if os.name == 'nt':
                os.startfile(folder_path)
            else:
                messagebox.showerror("Error", "Unsupported OS.")
        except Exception as e:
            messagebox.showerror("Error", f"{self.translate('stream_status_error')} {e}")

    def delete_stream_file(self, file_path):
        """
        刪除單一 stream 檔案，並提示確認。
        
        alias: delete_stream_file
        parameter: file_path (str)
        """
        confirm = messagebox.askyesno(self.translate("stream_confirm_delete_title"), f"{self.translate('stream_confirm_delete_message')}\n{file_path}")
        if not confirm:
            return
        try:
            os.remove(file_path)
            messagebox.showinfo("Success", self.translate("stream_success_delete", 1))
            self.update_stream_tree_after_delete(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"{self.translate('stream_error_delete').format(file_path)}\n{e}")

    def update_stream_tree_after_delete(self, file_path):
        """
        Update the stream TreeView after deleting a file.
        
        alias: update_stream_tree_after_delete
        parameter: file_path (str)
        """
        basename = os.path.basename(file_path)
        rel_loc = os.path.relpath(os.path.dirname(file_path), self.stream_root_directory.get())
        for item in self.stream_tree.get_children():
            if self.stream_tree.set(item, "duplicate_file") == basename:
                locations_str = self.stream_tree.set(item, "locations")
                locations = locations_str.split('; ')
                if rel_loc in locations:
                    locations.remove(rel_loc)
                    if len(locations) <= 1:
                        self.stream_tree.delete(item)
                        self.stream_checker.duplicate_files.pop(basename, None)
                    else:
                        new_loc_str = '; '.join(locations)
                        self.stream_tree.set(item, "locations", new_loc_str)
                break

    def delete_all_stream_duplicates(self, duplicate_file, locations):
        """
        Delete all duplicates of a given file at multiple locations.
        
        alias: delete_all_stream_duplicates
        parameter: duplicate_file (str)
        parameter: locations (List[str])
        """
        confirm = messagebox.askyesno(self.translate("stream_confirm_delete_title"), f"{self.translate('stream_confirm_delete_message')}\n{duplicate_file}")
        if not confirm:
            return
        deleted = []
        failed = []
        for loc in locations:
            full_path = os.path.join(self.stream_root_directory.get(), loc, duplicate_file)
            try:
                os.remove(full_path)
                deleted.append(full_path)
            except Exception as e:
                failed.append((full_path, str(e)))
        if deleted:
            messagebox.showinfo("Success", self.translate("stream_success_delete", len(deleted)))
            for item in self.stream_tree.get_children():
                if self.stream_tree.set(item, "duplicate_file") == duplicate_file:
                    self.stream_tree.delete(item)
                    break
            self.stream_checker.duplicate_files.pop(duplicate_file, None)
        if failed:
            err_msg = "\n".join([f"{p}: {msg}" for p, msg in failed])
            messagebox.showerror("Error", self.translate("stream_error_delete", err_msg))
        self.status.set(self.translate("stream_status_completed"))

    def copy_stream_to_clipboard(self):
        """
        Copy the list of duplicate files to clipboard.
        
        alias: copy_stream_to_clipboard
        """
        duplicates = self.stream_checker.duplicate_files
        if not duplicates:
            messagebox.showinfo("Info", self.translate("stream_info_no_duplicates"))
            return
        try:
            lines = []
            for file, locs in duplicates.items():
                lines.append(f"{file}:")
                for loc in locs:
                    lines.append(loc)
                lines.append("")
            pyperclip.copy('\n'.join(lines))
            messagebox.showinfo("Success", self.translate("stream_info_copy_success"))
        except pyperclip.PyperclipException as e:
            messagebox.showerror("Error", f"{self.translate('stream_status_error')} {e}")

    def save_stream_to_file(self):
        """
        Save the list of duplicate files to a text file.
        
        alias: save_stream_to_file
        """
        duplicates = self.stream_checker.duplicate_files
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
                    for file, locs in duplicates.items():
                        f.write(f"{file}:\n")
                        for loc in locs:
                            f.write(f"{loc}\n")
                        f.write("\n")
                messagebox.showinfo("Success", self.translate("stream_info_save_success", file_path))
            except Exception as e:
                messagebox.showerror("Error", f"{self.translate('stream_status_error')} {e}")

    def select_all_stream(self):
        """
        Select (☑) all items in the stream TreeView.
        
        alias: select_all_stream
        """
        for item in self.stream_tree.get_children():
            self.stream_tree.set(item, "select", "☑")

    def sort_stream_tree(self, column):
        """
        Sort the stream TreeView by the specified column.
        
        alias: sort_stream_tree
        parameter: column (str)
        """
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_column = column

        def sort_key(item_id):
            return self.stream_tree.set(item_id, column).lower()

        sorted_items = sorted(self.stream_tree.get_children(), key=sort_key, reverse=self.sort_reverse)
        for idx, item_id in enumerate(sorted_items):
            self.stream_tree.move(item_id, '', idx)

    def check_manual_duplicates(self):
        """
        1. 讀取 txt_manual 中使用者貼上的「檔案清單」。
        2. 於 stream_root_directory 下搜尋所有檔案，
        建立「檔名 -> [所有絕對路徑]」的對照資料，
        再逐一比對使用者貼上的檔案清單：
            - 若存在一個副本則顯示路徑，
            - 若存在多個副本則標示重複並列出所有位置，
            - 若找不到則標示「NOT FOUND」。
        3. 將結果寫回 txt_manual (Text widget) 中。
        
        alias: check_manual_duplicates
        parameter: None
        """
        stream_root = self.stream_root_directory.get()
        if not stream_root:
            messagebox.showwarning("Warning", self.translate("stream_info_no_selected"))
            return

        if not os.path.isdir(stream_root):
            messagebox.showerror("Error", self.translate("stream_info_no_files"))
            return

        if not self.stream_checker:
            self.stream_checker = StreamDuplicateChecker(self.translator)

        user_text = self.txt_manual.get("1.0", tk.END)
        file_list = [line.strip() for line in user_text.splitlines() if line.strip()]

        self.txt_manual.delete("1.0", tk.END)
        self.txt_manual.insert(tk.END, f"{self.translate('manual_check_results')}\n\n")
        self.root.update_idletasks()

        all_stream_files = self.stream_checker.find_stream_files(stream_root)

        file_map = {}
        for fp in all_stream_files:
            basename = os.path.basename(fp)
            file_map.setdefault(basename, []).append(fp)

        result_lines = []
        for target_filename in file_list:
            if target_filename in file_map:
                found_locations = file_map[target_filename]
                if len(found_locations) == 1:
                    result_lines.append(f"{target_filename} -> {found_locations[0]}")
                else:
                    result_lines.append(f"{target_filename} ({self.translate('duplicates_label')})")
                    for loc in found_locations:
                        result_lines.append(f"   {loc}")
            else:
                result_lines.append(f"{target_filename} -> {self.translate('not_found')}")
        
        final_output = "\n".join(result_lines)
        self.txt_manual.insert(tk.END, final_output + "\n")

    def _thread_check_manual_duplicates(self):
        try:
            duplicates = self.stream_checker.scan_stream_duplicates(self.stream_root_directory.get())
            if duplicates:
                lines = []
                for file, locs in duplicates.items():
                    lines.append(f"{file}:")
                    for loc in locs:
                        lines.append(f"  {loc}")
                    lines.append("")
                result_text = "\n".join(lines)
            else:
                result_text = self.translate("stream_info_no_duplicates")
            self.root.after(0, self._update_text_manual, result_text)
            self.root.after(0, lambda: self.status.set(self.translate("stream_status_completed")))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"{self.translate('stream_status_error')} {e}"))
            self.root.after(0, lambda: self.status.set(self.translate("stream_status_error")))

    def _update_text_manual(self, text):
        """
        alias: _update_text_manual
        parameter: text (str)
        """
        self.txt_manual.delete("1.0", tk.END)
        self.txt_manual.insert(tk.END, text)

    # --------------------#
    # Language Switching
    # --------------------#
    def change_language(self, event=None):
        """
        Event handler for language combobox selection.
        
        alias: change_language
        parameter: event (Event)
        """
        lang = self.language_var.get()
        self.set_language(lang)
        # Refresh tab labels
        self.notebook.tab(0, text=self.translate("title"))
        self.notebook.tab(1, text=self.translate("stream_tab"))
        self.status.set(self.translate("status_ready"))
        # For a complete multi-language solution, 
        # re-building or dynamically updating all UI text is recommended.

    # --------------------#
    # Main Entry
    # --------------------#
    @staticmethod
    def main():
        """
        Main entry point to run the Tkinter application.
        
        alias: main
        """
        root = tk.Tk()
        app = GUI_MAIN(root)
        root.mainloop()

if __name__ == "__main__":
    GUI_MAIN.main()