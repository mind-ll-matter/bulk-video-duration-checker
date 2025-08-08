#!/usr/bin/env python3
"""
MP4 Duration Calculator

This script searches through all MP4 files in a specified folder and its subfolders,
then calculates and displays the total duration of all videos combined, as well as
the total duration within each subfolder.
"""

import os
import sys
from pathlib import Path
from moviepy.editor import VideoFileClip
import time
from collections import defaultdict
import argparse
from datetime import datetime
import io
import contextlib


def format_duration(seconds):
    """Convert seconds to a human-readable format (HH:MM:SS)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_video_duration(file_path):
    """Get the duration of a video file in seconds"""
    try:
        # Convert Path object to string for moviepy
        file_path_str = str(file_path)
        with VideoFileClip(file_path_str) as clip:
            return clip.duration
    except Exception as e:
        error_msg = f"Error reading {file_path}: {e}"
        print(error_msg)
        return 0, error_msg


def get_video_duration_alternative(file_path):
    """Alternative method to get video duration using ffprobe if available"""
    try:
        import subprocess
        import json
        
        # Try using ffprobe (part of ffmpeg) if available
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', str(file_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            return duration
    except Exception:
        pass
    
    return 0


def find_mp4_files(folder_path):
    """Recursively find all MP4 files in the given folder and its subfolders"""
    mp4_files = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return []
    
    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return []
    
    print(f"Searching recursively in: {folder.absolute()}")
    
    # Search for MP4 files recursively
    for file_path in folder.rglob("*.mp4"):
        if file_path.is_file():
            mp4_files.append(file_path)
            # Show the relative path to help debug
            relative_path = file_path.relative_to(folder)
            print(f"  Found: {relative_path}")
    
    return mp4_files


def count_mp4_files_quiet(folder_path):
    """Count MP4 files recursively without printing."""
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        return 0
    return sum(1 for _ in folder.rglob("*.mp4"))


def calculate_subfolder_durations(folder_path, mp4_files):
    """Calculate duration totals for each subfolder"""
    folder = Path(folder_path)
    subfolder_totals = defaultdict(float)
    subfolder_counts = defaultdict(int)
    subfolder_files = defaultdict(list)
    
    for file_path in mp4_files:
        relative_path = file_path.relative_to(folder)
        # Get the subfolder (parent of the file)
        subfolder = relative_path.parent
        
        # Use the subfolder name, or "Root" if it's in the main folder
        subfolder_name = str(subfolder) if str(subfolder) != "." else "Root"
        
        # Get duration
        result = get_video_duration(file_path)
        if isinstance(result, tuple):
            duration, _ = result
        else:
            duration = result
            
        if duration <= 0:
            # Try alternative method
            duration = get_video_duration_alternative(file_path)
        
        if duration > 0:
            subfolder_totals[subfolder_name] += duration
            subfolder_counts[subfolder_name] += 1
            subfolder_files[subfolder_name].append((relative_path, duration))
    
    return subfolder_totals, subfolder_counts, subfolder_files


def calculate_total_duration(folder_path):
    """Calculate the total duration of all MP4 files in the folder and subfolders"""
    print(f"Searching for MP4 files in: {folder_path}")
    print("-" * 50)
    
    # Find all MP4 files
    mp4_files = find_mp4_files(folder_path)
    
    if not mp4_files:
        print("No MP4 files found in the specified folder and its subfolders.")
        return
    
    print(f"Found {len(mp4_files)} MP4 file(s):")
    print()
    
    # Calculate subfolder durations first
    subfolder_totals, subfolder_counts, subfolder_files = calculate_subfolder_durations(folder_path, mp4_files)
    
    total_duration = 0
    file_count = 0
    error_messages = []
    
    # Process each MP4 file
    for i, file_path in enumerate(mp4_files, 1):
        relative_path = file_path.relative_to(Path(folder_path))
        print(f"[{i}/{len(mp4_files)}] Processing: {relative_path}")
        
        result = get_video_duration(file_path)
        if isinstance(result, tuple):
            duration, error_msg = result
            error_messages.append(error_msg)
        else:
            duration = result
            
        if duration > 0:
            total_duration += duration
            file_count += 1
            print(f"    Duration: {format_duration(duration)}")
        else:
            # Try alternative method
            print(f"    Trying alternative method...")
            duration = get_video_duration_alternative(file_path)
            if duration > 0:
                total_duration += duration
                file_count += 1
                print(f"    Duration: {format_duration(duration)} (alternative method)")
            else:
                print(f"    Skipped (could not read duration with any method)")
        print()
    
    # Display subfolder summaries
    print("=" * 50)
    print("SUBFOLDER SUMMARIES")
    print("=" * 50)
    
    # Sort subfolders alphabetically
    sorted_subfolders = sorted(subfolder_totals.items(), key=lambda x: x[0])
    
    for subfolder_name, total_duration_subfolder in sorted_subfolders:
        file_count_subfolder = subfolder_counts[subfolder_name]
        print(f"\n{subfolder_name}:")
        print(f"  Files: {file_count_subfolder}")
        print(f"  Average Duration: {format_duration(total_duration_subfolder / file_count_subfolder)}")
        print(f"  Total Duration: {format_duration(total_duration_subfolder)}")
        
        # # Show individual files in this subfolder
        # if file_count_subfolder <= 10:  # Only show if 10 or fewer files
        #     for file_path, duration in subfolder_files[subfolder_name]:
        #         print(f"    {file_path.name}: {format_duration(duration)}")
        # else:
        #     print(f"    (showing first 5 files)")
        #     for file_path, duration in subfolder_files[subfolder_name][:5]:
        #         print(f"    {file_path.name}: {format_duration(duration)}")
        #     print(f"    ... and {file_count_subfolder - 5} more files")
    
    # Display overall results
    print("\n" + "=" * 50)
    print("OVERALL SUMMARY")
    print("=" * 50)
    print(f"Total files processed: {len(mp4_files)}")
    print(f"Successful reads: {file_count}")
    print(f"Failed reads: {len(mp4_files) - file_count}")
    print()
    
    if error_messages:
        print("COMMON ERROR TYPES:")
        error_types = {}
        for msg in error_messages:
            if "OSError" in msg:
                error_types["OSError"] = error_types.get("OSError", 0) + 1
            elif "IndexError" in msg:
                error_types["IndexError"] = error_types.get("IndexError", 0) + 1
            elif "KeyError" in msg:
                error_types["KeyError"] = error_types.get("KeyError", 0) + 1
            else:
                error_types["Other"] = error_types.get("Other", 0) + 1
        
        for error_type, count in error_types.items():
            print(f"  {error_type}: {count} files")
        print()
    
    if total_duration > 0:
        print(f"Total duration: {format_duration(total_duration)}")
        print(f"Total duration (seconds): {total_duration:.2f}")
        print(f"Total duration (hours): {total_duration / 3600:.2f}")
    else:
        print("No valid video durations found.")


class _Tee:
    """Duplicate writes to two streams."""

    def __init__(self, stream_a, stream_b):
        self.stream_a = stream_a
        self.stream_b = stream_b

    def write(self, data):
        self.stream_a.write(data)
        self.stream_b.write(data)

    def flush(self):
        self.stream_a.flush()
        self.stream_b.flush()


def _extract_summary_from_output(full_text: str) -> str:
    """Return only the output from the 'SUBFOLDER SUMMARIES' section onward.

    Falls back to 'OVERALL SUMMARY' if the first marker isn't found.
    If neither is found, returns the original text.
    """
    lines = full_text.splitlines()
    marker = "SUBFOLDER SUMMARIES"
    idx = None

    for i, line in enumerate(lines):
        if line.strip() == marker:
            idx = i
            break

    if idx is None:
        alt_marker = "OVERALL SUMMARY"
        for i, line in enumerate(lines):
            if line.strip() == alt_marker:
                idx = i
                break

    if idx is None:
        return full_text

    start = idx
    if idx > 0 and set(lines[idx - 1].strip()) == {"="}:
        start = idx - 1

    summary_lines = lines[start:]
    # Preserve trailing newline if present in original
    trailing_newline = "\n" if full_text.endswith("\n") else ""
    return "\n".join(summary_lines) + trailing_newline


def main():
    """Main function to handle user input and run the duration calculation"""
    parser = argparse.ArgumentParser(description="Calculate total MP4 durations recursively.")
    parser.add_argument("folder", nargs="?", help="Folder path to search for MP4 files")
    parser.add_argument("--save", action="store_true", help="Save the output to a text file")
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory to store text reports (created if missing). Relative to script directory by default.",
    )
    args = parser.parse_args()

    print("MP4 Duration Calculator")
    print("=" * 30)
    print()

    # Get folder path from user or argument
    if args.folder:
        folder_path = args.folder
    else:
        folder_path = input("Enter the folder path to search for MP4 files: ").strip()
    
    # Remove quotes if user included them
    folder_path = folder_path.strip('"\'')
    
    if not folder_path:
        print("No folder path provided. Exiting.")
        return
    
    start_time = time.time()

    if args.save:
        # Capture all output printed by calculate_total_duration
        capture_buffer = io.StringIO()
        tee_stream = _Tee(sys.stdout, capture_buffer)
        with contextlib.redirect_stdout(tee_stream):
            calculate_total_duration(folder_path)
            end_time = time.time()
            print(f"\nScript execution time: {end_time - start_time:.2f} seconds")

        # Build output directory path relative to the script by default
        script_dir = Path(__file__).resolve().parent
        output_dir = Path(args.output_dir)
        if not output_dir.is_absolute():
            output_dir = script_dir / output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # Compose filename: <folderName>_<YYYYMMDD-HHMMSS>_<N>videos.txt
        analyzed_folder_name = Path(folder_path).resolve().name or "root"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        video_count = count_mp4_files_quiet(folder_path)
        safe_folder = analyzed_folder_name.replace(" ", "_")
        filename = f"{safe_folder}_{timestamp}_{video_count}videos.txt"
        report_path = output_dir / filename

        full_output = capture_buffer.getvalue()
        summary_output = _extract_summary_from_output(full_output)
        with report_path.open("w", encoding="utf-8") as f:
            f.write(summary_output)

        print(f"\nSaved report to: {report_path}")
    else:
        calculate_total_duration(folder_path)
        end_time = time.time()
        print(f"\nScript execution time: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
