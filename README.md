# Duplicate File Scanner

A powerful, efficient Python tool to find duplicate files across multiple folders. Supports content-based or filename-based comparison, with features like GUI folder selection, live progress, parallel processing, and colored output.

## Features

- **Content Comparison**: Find truly identical files by hashing their content (default mode).
- **Filename Comparison**: Quickly find files with the same name (faster, use `--by-name`).
- **GUI Support**: Use a graphical dialog to select folders (`--gui`).
- **Live Progress**: Real-time speed updates and progress bars during scanning.
- **Parallel Processing**: Multi-core hashing for faster performance.
- **Colored Output**: Visual sections and highlights (requires `colorama`).
- **Cross-Platform**: Works on Windows, macOS, and Linux.

## Installation

1. **Prerequisites**: Python 3.6+
2. **Clone or Download**: Place `file_comparison.py` in your directory.
3. **Install Dependencies** (optional, for full features):
   ```
   pip install colorama tqdm
   ```
   - `colorama`: For colored output.
   - `tqdm`: For progress bars.
   - `flask`: For web UI (future feature).

## Usage

### Basic Examples
```bash
# Scan by content (default)
python file_comparison.py "C:\folder1" "C:\folder2"

# Scan by filename
python file_comparison.py --by-name "C:\folder1" "C:\folder2"

# Use GUI to select folders
python file_comparison.py --gui

# Combine options
python file_comparison.py --by-name --gui
```

### Command-Line Options
- `folders`: Paths to folders to scan (optional if using `--gui`).
- `--by-name`: Compare by filename instead of content.
- `--gui`: Launch folder selection dialog.
- `--help`: Show detailed help and examples.

### Output
- **Scanning Phase**: Live progress with speed updates.
- **Results**: Grouped duplicates with paths.
- **Summary**: Total files, data processed, time, and speeds.

Example Output:
```
==================================================
DUPLICATE FILE SCANNER
==================================================
Starting scan...
Scanning folder: folder1 (0.00 MB/s)
...
Hashing files: 100%|██████████████████| 350/350 [00:05<00:00, 62.50it/s]
...
Duplicate files found (compared by content hash):
Duplicate Group 1 (content hash: abc123...):
  - folder1\file1.txt
  - folder2\file1.txt
...
==================================================
SUMMARY
==================================================
Data processed: 25.70 MB
Time taken: 5.46 seconds
File speed: 64.10 files/second
Data speed: 4.71 MB/second
```

## Requirements

- Python 3.6+
- Optional: `colorama`, `tqdm` (install via pip)

## Contributing

Feel free to submit issues or pull requests on GitHub.

## License

MIT License - see [LICENSE](LICENSE) for details.