import os
import hashlib
import sys
import argparse
import time
import threading
import multiprocessing
from collections import defaultdict
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

def print_speed_live(start_time, total_bytes_list, current_status):
    while True:
        elapsed = time.time() - start_time
        speed = total_bytes_list[0] / elapsed / (1024*1024) if elapsed > 0 else 0
        if "Scanning folder:" in current_status[0]:
            parts = current_status[0].rsplit(' (', 1)
            if len(parts) == 2:
                current_status[0] = f"{parts[0]} ({speed:.2f} MB/s)"
                print(f"\r{current_status[0]}", end='', flush=True)
        time.sleep(1)

def get_file_hash(filepath):
    """Compute MD5 hash of a file."""
    try:
        if os.path.getsize(filepath) == 0:
            return 'EMPTY'  # Special marker for empty files
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (OSError, IOError):
        return None

def find_duplicate_files(folders, by_name=False, start_time=None):
    """Find duplicate files across given folders based on content hash or filename."""
    file_groups = defaultdict(list)
    total_files = 0
    total_bytes = [0]  # list for thread-safe access
    current_status = [""]  # for live updates
    all_files = []  # collect all files for parallel processing
    seen = set()  # to avoid scanning same file multiple times
    
    speed_thread = threading.Thread(target=print_speed_live, args=(start_time, total_bytes, current_status), daemon=True)
    speed_thread.start()
    
    current_status[0] = "Starting scan..."
    print(current_status[0])
    for folder in folders:
        if not os.path.isdir(folder):
            print(f"Warning: {folder} is not a valid directory.")
            continue
        current_status[0] = f"Scanning folder: {folder} (0.00 MB/s)"
        print(current_status[0])
        folder_start = time.time()
        folder_files = 0
        folder_bytes = 0
        for root, dirs, files in os.walk(folder):
            for file in files:
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                total_bytes[0] += size
                folder_bytes += size
                real_path = os.path.realpath(filepath)
                if real_path not in seen:
                    seen.add(real_path)
                    all_files.append(filepath)
                folder_files += 1
                total_files += 1
                if total_files % 100 == 0 and start_time:
                    current_elapsed = time.time() - start_time
                    current_speed = total_bytes[0] / current_elapsed / (1024*1024) if current_elapsed > 0 else 0
                    print(f"Processed {total_files} files... Current data speed: {current_speed:.2f} MB/s")
        folder_elapsed = time.time() - folder_start
        speed = folder_bytes / folder_elapsed / (1024*1024) if folder_elapsed > 0 else 0
        print(f"\nFinished scanning {folder}: {folder_files} files found in {folder_elapsed:.2f} seconds ({folder_bytes / (1024*1024):.2f} MB, {speed:.2f} MB/s)")
        print("-" * 40)  # Separator between folders
    
    # Parallel hashing with progress bar
    if all_files:
        with multiprocessing.Pool() as pool:
            hashes = list(tqdm(pool.imap(get_file_hash, all_files), total=len(all_files), desc="Hashing files", disable=not HAS_TQDM))
        
        for i, filepath in enumerate(all_files):
            file_hash = hashes[i]
            if by_name:
                key = os.path.basename(filepath)
                file_groups[key].append(filepath)
            else:
                if file_hash is None:
                    print(f"Could not read: {filepath}")
                elif file_hash != 'EMPTY':
                    file_groups[file_hash].append(filepath)
    
    current_status[0] = ""  # stop updating
    print(f"\nScan complete. Total files processed: {total_files}")
    duplicates = {key: paths for key, paths in file_groups.items() if len(paths) > 1}
    return duplicates, total_files, total_bytes[0]

def main():
    parser = argparse.ArgumentParser(
        description="Duplicate File Scanner: Find identical files across folders by content or filename. "
                    "Supports GUI selection, progress tracking, and parallel processing for efficiency.",
        epilog="""
Examples:
  python file_comparison.py "C:\\folder1" "C:\\folder2"                    # Scan by content (default)
  python file_comparison.py --by-name "C:\\folder1" "C:\\folder2"          # Scan by filename
  python file_comparison.py --gui                                         # Use GUI to select folders
  python file_comparison.py --by-name --gui                               # GUI with filename comparison

Tips for first-time users:
- Use --gui if you prefer a file dialog over typing paths.
- Content comparison (default) finds truly identical files; filename comparison finds same-named files.
- Progress is shown live; large scans may take time but provide real-time updates.
- Results are grouped for easy review.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('folders', nargs='*', help='Paths to folders to scan (leave empty to use GUI)')
    parser.add_argument('--by-name', action='store_true', help='Compare files by filename instead of content (faster, but less accurate)')
    parser.add_argument('--gui', action='store_true', help='Launch a graphical dialog to select folders (requires Tkinter)')
    args = parser.parse_args()
    
    if args.gui or not args.folders:
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            folders = []
            while True:
                folder = filedialog.askdirectory(title="Select a folder to scan (Cancel to finish)")
                if not folder:
                    break
                folders.append(folder)
            if not folders:
                print("No folders selected. Exiting.")
                sys.exit(1)
            args.folders = folders
        except ImportError:
            print("Tkinter not available. Please provide folders as arguments.")
            sys.exit(1)
    
    header_color = Fore.CYAN + Style.BRIGHT if HAS_COLORAMA else ''
    result_color = Fore.GREEN if HAS_COLORAMA else ''
    summary_color = Fore.YELLOW if HAS_COLORAMA else ''
    error_color = Fore.RED if HAS_COLORAMA else ''
    
    print(header_color + "=" * 50)
    print(header_color + "DUPLICATE FILE SCANNER")
    print(header_color + "=" * 50)
    start_time = time.time()
    duplicates, total_files, total_bytes = find_duplicate_files(args.folders, by_name=args.by_name, start_time=start_time)
    elapsed = time.time() - start_time
    
    print("\n" + result_color + "=" * 50)
    print(result_color + "RESULTS")
    print(result_color + "=" * 50)
    if not duplicates:
        mode = "name" if args.by_name else "content"
        print(f"No duplicate files found across the given folders (compared by {mode}).")
    else:
        mode = "name" if args.by_name else "content hash"
        print(f"Duplicate files found (compared by {mode}):")
        dup_count = 0
        for key, paths in duplicates.items():
            dup_count += 1
            print(f"\nDuplicate Group {dup_count} ({mode}: {key}):")
            for path in paths:
                print(f"  - {path}")
        print(f"\nTotal duplicate groups: {dup_count}")
    
    print("\n" + summary_color + "=" * 50)
    print(summary_color + "SUMMARY")
    print(summary_color + "=" * 50)
    print(f"Data processed: {total_bytes / (1024*1024):.2f} MB")
    print(f"Time taken: {elapsed:.2f} seconds")
    if total_files > 0:
        print(f"File speed: {total_files / elapsed:.2f} files/second")
    if total_bytes > 0:
        print(f"Data speed: {total_bytes / elapsed / (1024*1024):.2f} MB/second")
    print(summary_color + "=" * 50)

if __name__ == "__main__":
    main()