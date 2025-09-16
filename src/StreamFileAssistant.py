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

# -------------------------#
# 1. YFT Cleaner Logic
# -------------------------#
class YftCleaner:
    """
    A class dedicated to handling YFT ( *_hi.yft ) file scanning, size and status checking, deletion, etc.
    """
    def __init__(self, size_margin_kb: float = 0.0):
        self.deletable_files = []
        self.size_margin_kb = size_margin_kb

    def find_hi_yft_files(self, root_dir: str):
        """
        Recursively find all `*_hi.yft` files in any 'stream' folder under root_dir.
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
        Performs logic for a given hi_file
        """
        original_file = self.get_original_file(hi_file)
        if not original_file or not os.path.isfile(original_file):
            return None

        hi_hash = self.compute_file_hash(hi_file)
        org_hash = self.compute_file_hash(original_file)

        diff_bytes = 0

        if hi_hash and org_hash and hi_hash == org_hash:
            return self._process_identical_files(hi_file, diff_bytes=0)

        if self.size_margin_kb > 0.0:
            size_hi_bytes = os.path.getsize(hi_file)
            size_org_bytes = os.path.getsize(original_file)
            diff_bytes = abs(size_hi_bytes - size_org_bytes)
            diff_kb = diff_bytes / 1024.0

            if diff_kb <= self.size_margin_kb:
                return self._process_identical_files(hi_file, diff_bytes=diff_bytes)

        return None

    def _process_identical_files(self, hi_file: str, diff_bytes: int):
        """
        Helper method to handle the rest of the logic if hi_file is considered identical to its original.
        """
        is_resource, physPages, virtPages = self.read_yft_header(hi_file)

        if is_resource:
            phys_size = self.convert_rsc7_size(physPages)
            virt_size = self.convert_rsc7_size(virtPages)
            phys_mb = phys_size / (1024.0 * 1024.0)
            virt_mb = virt_size / (1024.0 * 1024.0)
            size_str = f"PH:{phys_mb:.2f}/VR:{virt_mb:.2f} MB"
            max_mb = max(phys_mb, virt_mb)
            status = self.determine_status(max_mb)
            if status == "Critical Oversized":
                pass
            elif status in ["Warning", "Critical"]:
                status += " - Oversized assets can and WILL lead to streaming issues (such as models not loading/rendering)."
            else:
                status += " - good"
        else:
            actual_size = os.path.getsize(hi_file)
            actual_mb = actual_size / (1024.0 * 1024.0)
            size_str = f"{actual_mb:.2f} MB"
            status = self.determine_status(actual_mb)
            if status == "Critical Oversized":
                pass
            elif status in ["Warning", "Critical"]:
                status += " - Oversized assets can and WILL lead to streaming issues (such as models not loading/rendering)."
            else:
                status += " - Unknown format"

        if diff_bytes > 0:
            status += f" [Margin used: diff={diff_bytes} bytes]"

        return (hi_file, size_str, status)

    def get_original_file(self, hi_file: str):
        """
        Retrieve the original file corresponding to hi_file (replace '_hi' with '').
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
        """
        try:
            hash_func = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            print(f"Error: {e}")
            return None

    def read_yft_header(self, file_path: str):
        """
        Read the YFT file header.
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
            print(f"Error: {e}")
            return (False, 0, 0)

    def convert_rsc7_size(self, flags: int):
        """
        Convert flags to size in bytes.
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
        """
        if size_mb > 64:
            return "Critical Oversized"
        elif size_mb > 32:
            return "Critical"
        elif size_mb > 16:
            return "Warning"
        else:
            return "OK"


# ------------------------------------------#
# 2. Stream Duplicate Checker Logic
# ------------------------------------------#
class StreamDuplicateChecker:
    """
    A class dedicated to scanning and removing duplicate files in 'Stream' folders
    """
    def __init__(self):
        self.duplicate_files = {}
        self.critical_conflicts = {}

    def scan_stream_duplicates(self, stream_root_directory: str):
        """
        Scan 'stream_root_directory' for all 'stream' folders and gather all files.
        Only scan files within 'stream' directories for regular duplicates.
        """
        stream_files = self.find_stream_files(stream_root_directory)
        file_dict = {}
        
        for file in stream_files:
            filename = os.path.basename(file).lower()
            
            if filename not in file_dict:
                file_dict[filename] = [os.path.dirname(file)]
            else:
                file_dict[filename].append(os.path.dirname(file))

        duplicates = {k: v for k, v in file_dict.items() if len(v) > 1}
        self.duplicate_files = duplicates
                
        return duplicates

    def scan_critical_files(self, root_directory: str):
        """
        Scan for critical config files (.ymt, .meta, .xml) throughout the entire resource structure.
        This scans ALL directories, not just 'stream' folders.
        """
        critical_files = self.find_critical_files(root_directory)
        file_dict = {}
        
        for file in critical_files:
            filename = os.path.basename(file).lower()
            
            if filename not in file_dict:
                file_dict[filename] = [os.path.dirname(file)]
            else:
                file_dict[filename].append(os.path.dirname(file))
        
        # All critical files are stored, not just duplicates
        # This allows us to show which critical files exist and where
        self.critical_conflicts = file_dict
        
        return file_dict

    def find_critical_files(self, root_dir: str):
        """
        Recursively find all critical config files (.ymt, .meta, .xml) in ANY folder under root_dir.
        This does NOT restrict to 'stream' folders since config files often exist at resource root.
        """
        critical_files = []
        critical_extensions = {'.ymt', '.meta', '.xml'}
        
        root = Path(root_dir)
        
        # Scan ALL directories, not just stream folders
        for ext in critical_extensions:
            for file in root.rglob(f'*{ext}'):
                if file.is_file():
                    critical_files.append(str(file))
        
        return critical_files

    def is_critical_file(self, filename: str) -> bool:
        """
        Check if a file is a critical config file based on extension
        """
        filename_lower = filename.lower()
        critical_extensions = {'.ymt', '.meta', '.xml'}
        
        for ext in critical_extensions:
            if filename_lower.endswith(ext):
                return True
                
        return False
    
    def get_critical_file_type(self, filename: str) -> str:
        """
        Get the type/category of a critical file based on extension
        """
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.ymt'):
            # Special cases for specific YMT files
            if 'scenario' in filename_lower:
                return "Scenario File"
            elif 'manifest' in filename_lower:
                return "Manifest File"
            elif 'doortuning' in filename_lower:
                return "Door Tuning"
            elif 'vfxfogvolume' in filename_lower:
                return "VFX Fog Volume"
            else:
                return "YMT Config"
        elif filename_lower.endswith('.meta'):
            # Special cases for specific META files
            if 'gta5' in filename_lower:
                return "Game Metadata"
            elif 'gtxd' in filename_lower:
                return "Texture Dictionary"
            else:
                return "META Config"
        elif filename_lower.endswith('.xml'):
            # Special cases for specific XML files
            if 'water' in filename_lower:
                return "Water Config"
            else:
                return "XML Config"
        elif filename_lower.endswith('.ynv'):
            return "Navigation Mesh"
        elif filename_lower.endswith('.ynd'):
            return "Path Node"
        
        return "Config File"

    def find_stream_files(self, root_dir: str):
        """
        Recursively find all files in any 'stream' folders under root_dir.
        This is for regular duplicate checking, restricted to stream folders.
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
# 3. GUI and Main Controller
# ----------------------------------------#
class GUI_MAIN:
    """
    A class responsible for managing the entire Tkinter GUI
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Stream Files Assistant Extended")
        self.root.geometry("1280x800")
        self.root.resizable(True, True)

        # Margin-related variables
        self.enable_margin_var = tk.BooleanVar(value=False)
        self.size_margin_kb_var = tk.StringVar(value="0.0")

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
        
        # Critical files filter
        self.critical_filter_var = tk.StringVar(value="All Files")

        # Build UI
        self.setup_ui()

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
        self.notebook.add(self.tab_yft, text="Duplicate YFT Cleaner")
        self.setup_yft_tab()

        # Tab 2: Stream Duplicate Checker
        self.tab_stream = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_stream, text="Stream Duplicate Checker")
        self.setup_stream_tab()
        
        # Tab 3: Critical Config Files
        self.tab_critical = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_critical, text="Critical Config Files (.ymt/.meta/.xml)")
        self.setup_critical_tab()

        # Status bar
        self.status = tk.StringVar()
        self.status.set("Ready")
        lbl_status = ttk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor="w")
        lbl_status.pack(fill=tk.X, side=tk.BOTTOM)

        # Right-click menus
        self.yft_context_menu = tk.Menu(self.root, tearoff=0)
        self.yft_context_menu.add_command(label="View Folder", command=self.view_folder)

        self.stream_context_menu = tk.Menu(self.root, tearoff=0)
        
        self.critical_context_menu = tk.Menu(self.root, tearoff=0)

    def setup_yft_tab(self):
        frame_top = ttk.Frame(self.tab_yft, padding=10)
        frame_top.pack(fill=tk.X)

        lbl_dir = ttk.Label(frame_top, text="Root Directory:")
        lbl_dir.grid(row=0, column=0, sticky="w", padx=(0, 5))

        entry_dir = ttk.Entry(frame_top, textvariable=self.root_directory, width=60)
        entry_dir.grid(row=0, column=1, sticky="w", padx=(0, 5))

        btn_browse = ttk.Button(frame_top, text="Browse...", command=self.browse_directory)
        btn_browse.grid(row=0, column=2, sticky="w")

        # Margin UI
        frame_margin = ttk.Frame(self.tab_yft, padding=(10, 5))
        frame_margin.pack(fill=tk.X)

        check_margin = ttk.Checkbutton(
            frame_margin,
            text="Enable size margin (KB)",
            variable=self.enable_margin_var
        )
        check_margin.grid(row=0, column=0, sticky="w")

        entry_margin_kb = ttk.Entry(frame_margin, textvariable=self.size_margin_kb_var, width=10)
        entry_margin_kb.grid(row=0, column=1, padx=(5, 0), sticky="w")

        frame_scan = ttk.Frame(self.tab_yft, padding=10)
        frame_scan.pack(fill=tk.X)

        btn_scan = ttk.Button(frame_scan, text="Start Scan", command=self.start_scan)
        btn_scan.grid(row=0, column=0, sticky="w")

        self.progress = ttk.Progressbar(frame_scan, orient="horizontal", length=500, mode="determinate")
        self.progress.grid(row=0, column=1, padx=10, sticky="w")

        self.lbl_progress = ttk.Label(frame_scan, text="Progress: 0/0")
        self.lbl_progress.grid(row=0, column=2, sticky="w")

        frame_select_all = ttk.Frame(self.tab_yft, padding=(10, 0))
        frame_select_all.pack(fill=tk.X)
        btn_select_all = ttk.Button(frame_select_all, text="Select All", command=self.select_all_yft)
        btn_select_all.pack(anchor='w')

        frame_list = ttk.Frame(self.tab_yft, padding=10)
        frame_list.pack(fill=tk.BOTH, expand=True)

        scrollbar_yft = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
        scrollbar_yft.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("select", "model_name", "path", "size", "status")
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings", selectmode="none")
        self.tree.heading("select", text="Select", command=lambda: self.sort_tree("select"))
        self.tree.heading("model_name", text="Model Name", command=lambda: self.sort_tree("model_name"))
        self.tree.heading("path", text="File Path", command=lambda: self.sort_tree("path"))
        self.tree.heading("size", text="Size (MB)", command=lambda: self.sort_tree("size"))
        self.tree.heading("status", text="Oversize?", command=lambda: self.sort_tree("status"))

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
        btn_copy = ttk.Button(frame_actions, text="Copy List to Clipboard", command=self.copy_to_clipboard_yft)
        btn_copy.pack(side=tk.LEFT, padx=5)
        btn_save = ttk.Button(frame_actions, text="Save List to File", command=self.save_to_file_yft)
        btn_save.pack(side=tk.LEFT, padx=5)
        btn_delete = ttk.Button(frame_actions, text="Delete Selected Files", command=self.delete_selected_files_yft)
        btn_delete.pack(side=tk.LEFT, padx=5)

    def setup_stream_tab(self):
        frame_top = ttk.Frame(self.tab_stream, padding=10)
        frame_top.pack(fill=tk.X)

        lbl_dir = ttk.Label(frame_top, text="Stream Root Directory:")
        lbl_dir.grid(row=0, column=0, sticky="w", padx=(0, 5))

        entry_dir = ttk.Entry(frame_top, textvariable=self.stream_root_directory, width=60)
        entry_dir.grid(row=0, column=1, sticky="w", padx=(0, 5))

        btn_browse = ttk.Button(frame_top, text="Browse...", command=self.browse_stream_directory)
        btn_browse.grid(row=0, column=2, sticky="w")

        frame_scan = ttk.Frame(self.tab_stream, padding=10)
        frame_scan.pack(fill=tk.X)

        btn_scan_all = ttk.Button(frame_scan, text="Scan for Duplicates", command=self.start_stream_scan)
        btn_scan_all.grid(row=0, column=0, sticky="w", padx=(0, 5))

        self.stream_progress = ttk.Progressbar(frame_scan, orient="horizontal", length=400, mode="determinate")
        self.stream_progress.grid(row=0, column=1, padx=10, sticky="w")

        self.stream_lbl_progress = ttk.Label(frame_scan, text="Progress: 0/0")
        self.stream_lbl_progress.grid(row=0, column=2, sticky="w")

        frame_select_all = ttk.Frame(self.tab_stream, padding=(10, 0))
        frame_select_all.pack(fill=tk.X)
        btn_select_all_stream = ttk.Button(frame_select_all, text="Select All", command=self.select_all_stream)
        btn_select_all_stream.pack(anchor='w')

        frame_list = ttk.Frame(self.tab_stream, padding=10)
        frame_list.pack(fill=tk.BOTH, expand=True)

        scrollbar_stream = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
        scrollbar_stream.pack(side=tk.RIGHT, fill=tk.Y)

        stream_columns = ("select", "duplicate_file", "locations")
        self.stream_tree = ttk.Treeview(frame_list, columns=stream_columns, show="headings", selectmode="none")
        self.stream_tree.heading("select", text="Select", command=lambda: self.sort_stream_tree("select"))
        self.stream_tree.heading("duplicate_file", text="Duplicate File Name", command=lambda: self.sort_stream_tree("duplicate_file"))
        self.stream_tree.heading("locations", text="Locations", command=lambda: self.sort_stream_tree("locations"))

        self.stream_tree.column("select", width=50, anchor="center")
        self.stream_tree.column("duplicate_file", width=200, anchor="w")
        self.stream_tree.column("locations", width=600, anchor="w")

        self.stream_tree.configure(yscrollcommand=scrollbar_stream.set)
        scrollbar_stream.config(command=self.stream_tree.yview)

        self.stream_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.stream_tree.bind('<Button-1>', self.handle_click_stream)
        self.stream_tree.bind('<Button-3>', self.show_stream_context_menu)

        frame_actions = ttk.Frame(self.tab_stream, padding=10)
        frame_actions.pack(fill=tk.X)
        btn_copy = ttk.Button(frame_actions, text="Copy Duplicates to Clipboard", command=self.copy_stream_to_clipboard)
        btn_copy.pack(side=tk.LEFT, padx=5)
        btn_save = ttk.Button(frame_actions, text="Save Duplicates to File", command=self.save_stream_to_file)
        btn_save.pack(side=tk.LEFT, padx=5)

        frame_manual = ttk.Frame(self.tab_stream, padding=10)
        frame_manual.pack(fill=tk.BOTH, expand=True)

        btn_manual_check = ttk.Button(frame_manual, text="Manually Check for Duplicates", command=self.check_manual_duplicates)
        btn_manual_check.pack(anchor="e", pady=5)

        self.txt_manual = tk.Text(frame_manual, height=10)
        self.txt_manual.pack(fill=tk.BOTH, expand=True)

    def setup_critical_tab(self):
        """Setup the Critical Config Files tab"""
        # Info label
        frame_info = ttk.Frame(self.tab_critical, padding=10)
        frame_info.pack(fill=tk.X)
        
        info_label = ttk.Label(frame_info, text="Config files (.ymt, .meta & water.xml) should only exist once across the server:", 
                              font=('Calibri', 11, 'italic'))
        info_label.pack(anchor='w')
        
        # Note about scanning location
        note_label = ttk.Label(frame_info, 
                              text="Note: This scans ALL directories (not just within 'stream' folders) to find duplicate files.", 
                              font=('Calibri', 10, 'italic'), foreground='red')
        note_label.pack(anchor='w', pady=(5, 0))
        
        # Directory selection
        frame_top = ttk.Frame(self.tab_critical, padding=10)
        frame_top.pack(fill=tk.X)

        lbl_dir = ttk.Label(frame_top, text="Root Directory:")
        lbl_dir.grid(row=0, column=0, sticky="w", padx=(0, 5))

        # Use same directory variable as stream tab for consistency
        entry_dir = ttk.Entry(frame_top, textvariable=self.stream_root_directory, width=60)
        entry_dir.grid(row=0, column=1, sticky="w", padx=(0, 5))

        btn_browse = ttk.Button(frame_top, text="Browse...", 
                                command=self.browse_stream_directory)
        btn_browse.grid(row=0, column=2, sticky="w")

        # Scan controls
        frame_scan = ttk.Frame(self.tab_critical, padding=10)
        frame_scan.pack(fill=tk.X)

        btn_scan_critical = ttk.Button(frame_scan, text="Scan Critical Files", 
                                       command=self.scan_critical_files)
        btn_scan_critical.grid(row=0, column=0, sticky="w")

        self.critical_progress = ttk.Progressbar(frame_scan, orient="horizontal", 
                                                 length=400, mode="determinate")
        self.critical_progress.grid(row=0, column=1, padx=10, sticky="w")

        self.critical_lbl_progress = ttk.Label(frame_scan, text="Progress: 0/0")
        self.critical_lbl_progress.grid(row=0, column=2, sticky="w")

        # Filter controls
        frame_filter = ttk.Frame(self.tab_critical, padding=(10, 5))
        frame_filter.pack(fill=tk.X)
        
        lbl_filter = ttk.Label(frame_filter, text="Filter:")
        lbl_filter.pack(side=tk.LEFT, padx=(0, 5))
        
        filter_combo = ttk.Combobox(frame_filter, textvariable=self.critical_filter_var, 
                                    state="readonly", width=20)
        filter_combo['values'] = ["All Files", "Conflicts Only"]
        filter_combo.set("All Files")
        filter_combo.pack(side=tk.LEFT)
        filter_combo.bind("<<ComboboxSelected>>", self.filter_critical_view)

        # TreeView for critical files
        frame_list = ttk.Frame(self.tab_critical, padding=10)
        frame_list.pack(fill=tk.BOTH, expand=True)

        scrollbar_critical = ttk.Scrollbar(frame_list, orient=tk.VERTICAL)
        scrollbar_critical.pack(side=tk.RIGHT, fill=tk.Y)

        critical_columns = ("type", "file", "locations", "status")
        self.critical_tree = ttk.Treeview(frame_list, columns=critical_columns, 
                                          show="headings", selectmode="browse")
        self.critical_tree.heading("type", text="File Type")
        self.critical_tree.heading("file", text="File Name")
        self.critical_tree.heading("locations", text="Locations")
        self.critical_tree.heading("status", text="Status")

        self.critical_tree.column("type", width=150, anchor="w")
        self.critical_tree.column("file", width=250, anchor="w")
        self.critical_tree.column("locations", width=500, anchor="w")
        self.critical_tree.column("status", width=200, anchor="center")

        self.critical_tree.configure(yscrollcommand=scrollbar_critical.set)
        scrollbar_critical.config(command=self.critical_tree.yview)

        self.critical_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.critical_tree.bind('<Button-3>', self.show_critical_context_menu)

        # Action buttons
        frame_actions = ttk.Frame(self.tab_critical, padding=10)
        frame_actions.pack(fill=tk.X)
        
        btn_copy = ttk.Button(frame_actions, text="Copy Conflicts to Clipboard", 
                             command=self.copy_critical_conflicts)
        btn_copy.pack(side=tk.LEFT, padx=5)
        
        btn_save = ttk.Button(frame_actions, text="Save Conflicts Report", 
                             command=self.save_critical_report)
        btn_save.pack(side=tk.LEFT, padx=5)

    def scan_critical_files(self):
        """Scan for critical config files"""
        if not self.stream_root_directory.get():
            messagebox.showwarning("Warning", "No directory selected.")
            return
        if not os.path.isdir(self.stream_root_directory.get()):
            messagebox.showerror("Error", "No directory or invalid path selected.")
            return

        # Clear existing entries
        for item in self.critical_tree.get_children():
            self.critical_tree.delete(item)
            
        if not self.stream_checker:
            self.stream_checker = StreamDuplicateChecker()

        self.critical_progress["value"] = 0
        self.critical_lbl_progress.config(text="Progress: 0/0")
        self.status.set("Scanning...")

        threading.Thread(target=self.scan_critical_thread, daemon=True).start()

    def scan_critical_thread(self):
        """Background thread for scanning critical files"""
        try:
            # Scan for critical files (not restricted to stream folders)
            critical_files = self.stream_checker.scan_critical_files(self.stream_root_directory.get())
            
            # Update progress
            self.critical_progress["value"] = 100
            self.critical_lbl_progress.config(text="Scan Completed.")
            
            # Populate the tree
            self.populate_critical_tree()
            
            if critical_files:
                conflicts = sum(1 for locs in critical_files.values() if len(locs) > 1)
                total_files = len(critical_files)
                if conflicts > 0:
                    self.status.set(f"Scan Completed. - Found {total_files} critical files, {conflicts} have conflicts!")
                else:
                    self.status.set(f"Scan Completed. - Found {total_files} critical files, no conflicts.")
            else:
                self.status.set("No critical file conflicts found.")
                
        except Exception as e:
            self.status.set(f"Error: {e}")

    def populate_critical_tree(self):
        """Populate the critical files tree view"""
        stream_root = self.stream_root_directory.get()
        
        for filename, locations in self.stream_checker.critical_conflicts.items():
            file_type = self.stream_checker.get_critical_file_type(filename)
            
            # Convert locations to relative paths
            relative_locations = []
            for loc in locations:
                try:
                    rel_loc = os.path.relpath(loc, stream_root)
                except ValueError:
                    rel_loc = loc
                relative_locations.append(rel_loc)
            
            loc_str = '; '.join(relative_locations)
            
            # Determine status
            if len(locations) > 1:
                status = "CONFLICT - Multiple instances found!"
                tag = "conflict"
            else:
                status = "OK - Single instance"
                tag = "ok"
            
            item_id = self.critical_tree.insert("", tk.END, 
                                                values=(file_type, filename, loc_str, status),
                                                tags=(tag,))
            
        # Configure tags
        self.critical_tree.tag_configure("conflict", background="lightcoral")
        self.critical_tree.tag_configure("ok", background="lightgreen")

    def filter_critical_view(self, event=None):
        """Filter the critical files view"""
        filter_value = self.critical_filter_var.get()
        
        # Clear and repopulate based on filter
        for item in self.critical_tree.get_children():
            self.critical_tree.delete(item)
            
        if not self.stream_checker or not self.stream_checker.critical_conflicts:
            return
            
        stream_root = self.stream_root_directory.get()
        
        for filename, locations in self.stream_checker.critical_conflicts.items():
            # Apply filter
            if filter_value == "Conflicts Only" and len(locations) <= 1:
                continue
                
            file_type = self.stream_checker.get_critical_file_type(filename)
            
            relative_locations = []
            for loc in locations:
                try:
                    rel_loc = os.path.relpath(loc, stream_root)
                except ValueError:
                    rel_loc = loc
                relative_locations.append(rel_loc)
            
            loc_str = '; '.join(relative_locations)
            
            if len(locations) > 1:
                status = "CONFLICT - Multiple instances found!"
                tag = "conflict"
            else:
                status = "OK - Single instance"
                tag = "ok"
            
            item_id = self.critical_tree.insert("", tk.END, 
                                                values=(file_type, filename, loc_str, status),
                                                tags=(tag,))
        
        self.critical_tree.tag_configure("conflict", background="lightcoral")
        self.critical_tree.tag_configure("ok", background="lightgreen")

    def show_critical_context_menu(self, event):
        """Show context menu for critical files"""
        row_id = self.critical_tree.identify_row(event.y)
        if row_id:
            self.critical_tree.selection_set(row_id)
            self.right_clicked_row = row_id
            
            # Clear and rebuild menu
            self.critical_context_menu.delete(0, tk.END)
            
            filename = self.critical_tree.set(row_id, "file")
            locations_str = self.critical_tree.set(row_id, "locations")
            locations = locations_str.split('; ')
            
            # Add view folder options
            for loc in locations:
                full_path = os.path.join(self.stream_root_directory.get(), loc, filename)
                self.critical_context_menu.add_command(
                    label=f"📁 {loc}",
                    command=lambda path=full_path: self.open_folder_for_stream_file(path)
                )
                
            # If conflict, add delete options
            if len(locations) > 1:
                self.critical_context_menu.add_separator()
                for loc in locations:
                    full_path = os.path.join(self.stream_root_directory.get(), loc, filename)
                    self.critical_context_menu.add_command(
                        label=f"🗑️ Delete {loc}",
                        command=lambda path=full_path: self.delete_critical_file(path)
                    )
                    
            self.critical_context_menu.post(event.x_root, event.y_root)

    def delete_critical_file(self, file_path):
        """Delete a critical file with confirmation"""
        filename = os.path.basename(file_path)
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Delete critical config file: {filename}?\n\n"
            f"⚠️ This file may be required for proper resource operation.\n"
            f"Path: {file_path}"
        )
        if not confirm:
            return
            
        try:
            os.remove(file_path)
            messagebox.showinfo("Success", f"Deleted: {filename}")
            # Refresh the view
            self.scan_critical_files()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete {filename}:\n{e}")

    def copy_critical_conflicts(self):
        """Copy critical conflicts to clipboard"""
        conflicts = []
        for item in self.critical_tree.get_children():
            status = self.critical_tree.set(item, "status")
            if "CONFLICT" in status:
                filename = self.critical_tree.set(item, "file")
                file_type = self.critical_tree.set(item, "type")
                locations = self.critical_tree.set(item, "locations")
                conflicts.append(f"{file_type}: {filename}\nLocations: {locations}\n")
        
        if conflicts:
            try:
                pyperclip.copy('\n'.join(conflicts))
                messagebox.showinfo("Success", "Critical conflicts list copied to clipboard.")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
        else:
            messagebox.showinfo("Info", "No critical file conflicts found.")

    def save_critical_report(self):
        """Save critical files report to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Conflicts Report"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("Critical Config Files Report (.ymt/.meta/.xml)\n")
                f.write("=" * 50 + "\n\n")
                
                # Write conflicts first
                f.write("CONFLICTS (Files with multiple instances):\n")
                f.write("-" * 40 + "\n")
                conflicts_found = False
                
                for item in self.critical_tree.get_children():
                    status = self.critical_tree.set(item, "status")
                    if "CONFLICT" in status:
                        conflicts_found = True
                        filename = self.critical_tree.set(item, "file")
                        file_type = self.critical_tree.set(item, "type")
                        locations = self.critical_tree.set(item, "locations")
                        f.write(f"\n{file_type}: {filename}\n")
                        f.write(f"Locations:\n")
                        for loc in locations.split('; '):
                            f.write(f"  - {loc}\n")
                
                if not conflicts_found:
                    f.write("No conflicts found.\n")
                
                # Write OK files
                f.write("\n\nOK FILES (Single instances):\n")
                f.write("-" * 40 + "\n")
                
                for item in self.critical_tree.get_children():
                    status = self.critical_tree.set(item, "status")
                    if "OK" in status:
                        filename = self.critical_tree.set(item, "file")
                        file_type = self.critical_tree.set(item, "type")
                        locations = self.critical_tree.set(item, "locations")
                        f.write(f"{file_type}: {filename} -> {locations}\n")
                
            messagebox.showinfo("Success", f"Critical conflicts report saved to {file_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    # YFT Cleaner Events
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.root_directory.set(directory)

    def start_scan(self):
        if self.enable_margin_var.get():
            try:
                margin_kb = float(self.size_margin_kb_var.get())
            except ValueError:
                margin_kb = 0.0
        else:
            margin_kb = 0.0

        self.yft_cleaner = YftCleaner(size_margin_kb=margin_kb)

        if not self.root_directory.get():
            messagebox.showwarning("Warning", "No files selected.")
            return
        if not os.path.isdir(self.root_directory.get()):
            messagebox.showerror("Error", "No files available.")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.yft_cleaner.deletable_files.clear()
        self.total_files = 0
        self.processed_files = 0
        self.progress["value"] = 0
        self.lbl_progress.config(text="Progress: 0/0")
        self.status.set("Scanning...")

        threading.Thread(target=self.scan_files_thread, daemon=True).start()

    def scan_files_thread(self):
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
            self.status.set("Scan Completed.")
        except Exception as e:
            self.status.set(f"Error: {e}")

    def update_progress(self):
        if self.total_files > 0:
            progress_percent = (self.processed_files / self.total_files) * 100
            self.progress["value"] = progress_percent
            self.lbl_progress.config(text=f"Progress: {self.processed_files}/{self.total_files}")
        self.root.update_idletasks()

    def populate_treeview_yft(self, file_info_list):
        root_dir = self.root_directory.get()
        for file_path, size_str, status in file_info_list:
            model_name = os.path.basename(file_path)
            dir_path = os.path.dirname(file_path)
            try:
                relative_path = os.path.relpath(dir_path, root_dir)
            except ValueError:
                relative_path = dir_path

            item_id = self.tree.insert("", tk.END, values=("☐", model_name, relative_path, size_str, status))
            if status.startswith("OK"):
                self.tree.item(item_id, tags=("ok",))
                self.tree.tag_configure("ok", background="lightgreen")
            elif status.startswith("Warning"):
                self.tree.item(item_id, tags=("warning",))
                self.tree.tag_configure("warning", background="yellow")
            elif status.startswith("Critical"):
                self.tree.item(item_id, tags=("critical",))
                self.tree.tag_configure("critical", background="red")
            elif status.startswith("Critical Oversized"):
                self.tree.item(item_id, tags=("oversize",))
                self.tree.tag_configure("oversize", background="orange")
            else:
                self.tree.tag_configure("default", background="white")
                self.tree.item(item_id, tags=("default",))

    def handle_click_yft(self, event):
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
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.right_clicked_row = row_id
            self.yft_context_menu.post(event.x_root, event.y_root)
        else:
            self.right_clicked_row = None

    def view_folder(self):
        if self.right_clicked_row:
            path_val = self.tree.set(self.right_clicked_row, "path")
            model_name = self.tree.set(self.right_clicked_row, "model_name")
            full_path = os.path.join(self.root_directory.get(), path_val, model_name)
            folder_path = os.path.dirname(full_path)
        else:
            selected = self.get_selected_files_yft()
            if not selected:
                messagebox.showinfo("Info", "No files selected.")
                return
            folder_path = os.path.dirname(selected[0])

        try:
            if os.name == 'nt':
                os.startfile(folder_path)
            else:
                messagebox.showerror("Error", "Unsupported OS.")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def get_selected_files_yft(self):
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
        selected = self.get_selected_files_yft()
        if not selected:
            messagebox.showinfo("Info", "No files selected.")
            return
        try:
            pyperclip.copy('\n'.join(selected))
            messagebox.showinfo("Success", "File list copied to clipboard.")
        except pyperclip.PyperclipException as e:
            messagebox.showerror("Error", f"Error: {e}")

    def save_to_file_yft(self):
        selected = self.get_selected_files_yft()
        if not selected:
            messagebox.showinfo("Info", "No files selected.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save List to File"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(selected))
                messagebox.showinfo("Success", f"File list saved to {file_path}.")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

    def delete_selected_files_yft(self):
        selected_files = self.get_selected_files_yft()
        if not selected_files:
            messagebox.showinfo("Info", "No files selected.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the selected {len(selected_files)} files?")
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
            messagebox.showinfo("Success", f"Successfully deleted {len(deleted)} files.")
            self.yft_cleaner.deletable_files = [df for df in self.yft_cleaner.deletable_files if df[0] not in deleted]

        if failed:
            err_msg = "\n".join([f"{p}: {msg}" for p, msg in failed])
            messagebox.showerror("Error", f"Failed to delete the following files:\n{err_msg}")

        self.status.set("Scan Completed.")

    def select_all_yft(self):
        for item in self.tree.get_children():
            self.tree.set(item, "select", "☑")

    def sort_tree(self, column):
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

    # Stream Duplicate Checker Events
    def browse_stream_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.stream_root_directory.set(directory)

    def start_stream_scan(self):
        if not self.stream_root_directory.get():
            messagebox.showwarning("Warning", "No directory selected.")
            return
        if not os.path.isdir(self.stream_root_directory.get()):
            messagebox.showerror("Error", "No duplicate files found.")
            return

        for item in self.stream_tree.get_children():
            self.stream_tree.delete(item)
        if not self.stream_checker:
            self.stream_checker = StreamDuplicateChecker()

        self.stream_checker.duplicate_files.clear()
        self.total_stream_files = 0
        self.processed_stream_files = 0
        self.stream_progress["value"] = 0
        self.stream_lbl_progress.config(text="Progress: 0/0")
        self.status.set("Scanning...")

        threading.Thread(target=self.scan_stream_thread, daemon=True).start()

    def scan_stream_thread(self):
        try:
            all_files = self.stream_checker.find_stream_files(self.stream_root_directory.get())
            self.total_stream_files = len(all_files)
            duplicates = self.stream_checker.scan_stream_duplicates(self.stream_root_directory.get())
            self.processed_stream_files = self.total_stream_files
            self.update_stream_progress()
            
            if duplicates:
                self.populate_stream_treeview(duplicates)
                self.status.set("Scan Completed.")
            else:
                self.status.set("No duplicate files found.")
        except Exception as e:
            self.status.set(f"Error: {e}")

    def update_stream_progress(self):
        if self.total_stream_files > 0:
            p = (self.processed_stream_files / self.total_stream_files) * 100
            self.stream_progress["value"] = p
            self.stream_lbl_progress.config(text=f"Progress: {self.processed_stream_files}/{self.total_stream_files}")
        self.root.update_idletasks()

    def populate_stream_treeview(self, duplicates):
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
            
            # Highlight critical files
            if self.stream_checker.is_critical_file(file_name):
                self.stream_tree.tag_configure("critical_duplicate", background="lightyellow")
                self.stream_tree.item(item_id, tags=("critical_duplicate",))
            else:
                self.stream_tree.tag_configure("duplicate", background="lightcoral")
                self.stream_tree.item(item_id, tags=("duplicate",))

    def handle_click_stream(self, event):
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
        row_id = self.stream_tree.identify_row(event.y)
        if row_id:
            self.stream_tree.selection_set(row_id)
            self.right_clicked_row = row_id
            self.stream_context_menu.delete(0, tk.END)
            duplicate_file = self.stream_tree.set(row_id, "duplicate_file")
            locations_str = self.stream_tree.set(row_id, "locations")
            locations = locations_str.split('; ')
            
            # Check if it's a critical file
            if self.stream_checker.is_critical_file(duplicate_file):
                file_type = self.stream_checker.get_critical_file_type(duplicate_file)
                self.stream_context_menu.add_command(
                    label=f"⚠️ Critical File: {file_type}",
                    state=tk.DISABLED
                )
                self.stream_context_menu.add_separator()
            
            self.stream_context_menu.add_command(
                label="📂 View Folder",
                command=lambda: self.open_folder_for_stream(duplicate_file, locations[0] if locations else "")
            )
            self.stream_context_menu.add_separator()
            for loc in locations:
                full_path = os.path.join(self.stream_root_directory.get(), loc, duplicate_file)
                self.stream_context_menu.add_command(
                    label=f"📁 {loc}",
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
        path = os.path.join(self.stream_root_directory.get(), loc, duplicate_file)
        self.open_folder_for_stream_file(path)

    def open_folder_for_stream_file(self, file_path):
        folder_path = os.path.dirname(file_path)
        try:
            if os.name == 'nt':
                os.startfile(folder_path)
            else:
                messagebox.showerror("Error", "Unsupported OS.")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def delete_stream_file(self, file_path):
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the selected duplicate files?\n{file_path}")
        if not confirm:
            return
        try:
            os.remove(file_path)
            messagebox.showinfo("Success", f"Successfully deleted 1 duplicate files.")
            self.update_stream_tree_after_delete(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete the following duplicate files:\n{file_path}\n{e}")

    def update_stream_tree_after_delete(self, file_path):
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
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the selected duplicate files?\n{duplicate_file}")
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
            messagebox.showinfo("Success", f"Successfully deleted {len(deleted)} duplicate files.")
            for item in self.stream_tree.get_children():
                if self.stream_tree.set(item, "duplicate_file") == duplicate_file:
                    self.stream_tree.delete(item)
                    break
            self.stream_checker.duplicate_files.pop(duplicate_file, None)
        if failed:
            err_msg = "\n".join([f"{p}: {msg}" for p, msg in failed])
            messagebox.showerror("Error", f"Failed to delete the following duplicate files:\n{err_msg}")
        self.status.set("Scan Completed.")

    def copy_stream_to_clipboard(self):
        duplicates = self.stream_checker.duplicate_files
        if not duplicates:
            messagebox.showinfo("Info", "No duplicate files found.")
            return
        try:
            lines = []
            for file, locs in duplicates.items():
                if self.stream_checker.is_critical_file(file):
                    file_type = self.stream_checker.get_critical_file_type(file)
                    lines.append(f"{file} [{file_type}]:")
                else:
                    lines.append(f"{file}:")
                for loc in locs:
                    lines.append(loc)
                lines.append("")
            pyperclip.copy('\n'.join(lines))
            messagebox.showinfo("Success", "Duplicate file list copied to clipboard.")
        except pyperclip.PyperclipException as e:
            messagebox.showerror("Error", f"Error: {e}")

    def save_stream_to_file(self):
        duplicates = self.stream_checker.duplicate_files
        if not duplicates:
            messagebox.showinfo("Info", "No duplicate files found.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Duplicates to File"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for file, locs in duplicates.items():
                        if self.stream_checker.is_critical_file(file):
                            file_type = self.stream_checker.get_critical_file_type(file)
                            f.write(f"{file} [{file_type}]:\n")
                        else:
                            f.write(f"{file}:\n")
                        for loc in locs:
                            f.write(f"{loc}\n")
                        f.write("\n")
                messagebox.showinfo("Success", f"Duplicate file list saved to {file_path}.")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

    def select_all_stream(self):
        for item in self.stream_tree.get_children():
            self.stream_tree.set(item, "select", "☑")

    def sort_stream_tree(self, column):
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
        stream_root = self.stream_root_directory.get()
        if not stream_root:
            messagebox.showwarning("Warning", "No directory selected.")
            return

        if not os.path.isdir(stream_root):
            messagebox.showerror("Error", "No directory or invalid path selected.")
            return

        if not self.stream_checker:
            self.stream_checker = StreamDuplicateChecker()

        user_text = self.txt_manual.get("1.0", tk.END)
        file_list = [line.strip() for line in user_text.splitlines() if line.strip()]

        self.txt_manual.delete("1.0", tk.END)
        self.txt_manual.insert(tk.END, "Manual Check Results:\n\n")
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
                if self.stream_checker.is_critical_file(target_filename):
                    file_type = self.stream_checker.get_critical_file_type(target_filename)
                    result_lines.append(f"{target_filename} [{file_type}]:")
                else:
                    result_lines.append(f"{target_filename}:")
                    
                if len(found_locations) == 1:
                    result_lines.append(f"  -> {found_locations[0]}")
                else:
                    result_lines.append(f"  (Duplicate(s) Found in:)")
                    for loc in found_locations:
                        result_lines.append(f"     {loc}")
            else:
                result_lines.append(f"{target_filename} -> NOT FOUND")
        
        final_output = "\n".join(result_lines)
        self.txt_manual.insert(tk.END, final_output + "\n")

    @staticmethod
    def main():
        root = tk.Tk()
        app = GUI_MAIN(root)
        root.mainloop()

if __name__ == "__main__":
    GUI_MAIN.main()