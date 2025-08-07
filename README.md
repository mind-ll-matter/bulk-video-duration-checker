# MP4 Duration Calculator

This Python script searches through all MP4 files in a specified folder and its subfolders, then calculates and displays the total duration of all videos combined.

## Features

- Recursively searches through folders and subfolders for MP4 files
- Calculates individual and total video durations
- Displays results in multiple formats (HH:MM:SS, seconds, hours)
- Handles errors gracefully for corrupted or unreadable files
- Shows progress during processing
- Provides detailed summary statistics

## Installation

1. Make sure you have Python 3.6 or higher installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install moviepy
```

## Usage

### Method 1: Interactive Mode
Run the script without arguments and enter the folder path when prompted:

```bash
python mp4_duration_calculator.py
```

### Method 2: Command Line Argument
Provide the folder path as a command line argument:

```bash
python mp4_duration_calculator.py "C:\Users\YourName\Videos"
```

### Method 3: Drag and Drop (Windows)
You can also drag a folder onto the script file to analyze it.

## Output Example

```
MP4 Duration Calculator
==============================

Enter the folder path to search for MP4 files: C:\Videos

Searching for MP4 files in: C:\Videos
--------------------------------------------------
Found 3 MP4 file(s):

[1/3] Processing: video1.mp4
    Duration: 00:05:30

[2/3] Processing: video2.mp4
    Duration: 01:23:45

[3/3] Processing: video3.mp4
    Duration: 00:42:18

==================================================
SUMMARY
==================================================
Total files processed: 3
Successful reads: 3
Failed reads: 0

Total duration: 02:11:33
Total duration (seconds): 7893.00
Total duration (hours): 2.19

Script execution time: 3.45 seconds
```

## Notes

- The script uses the `moviepy` library to read video metadata
- Processing time depends on the number and size of video files
- Corrupted or unreadable files will be skipped with an error message
- The script handles both relative and absolute folder paths

## Troubleshooting

If you encounter issues:

1. Make sure `moviepy` is properly installed
2. Verify the folder path exists and contains MP4 files
3. Check that you have read permissions for the folder
4. For large video collections, the script may take some time to process all files
