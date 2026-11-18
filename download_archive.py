#!/usr/bin/env python3
"""
Internet Archive Download and GitHub Release Upload Script
Handles all processes from download to upload
"""

import os
import sys
import subprocess
import json
import requests
import re
from pathlib import Path
from typing import List, Optional

# Constants
MAX_FILE_SIZE = 1900 * 1024 * 1024  # 1.9GB in bytes
SPLIT_SIZE_MB = 1900


class ArchiveDownloader:
    def __init__(self, download_dir: str = "download"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def free_disk_space(self):
        """Process 1: Free disk space using jlumbroso/free-disk-space"""
        print("Process 1: Freeing disk space...")
        # This is handled by the GitHub Action, not by this script
        
    def install_packages(self):
        """Process 2: Install required packages"""
        print("Process 2: Installing packages...")
        # Handled by workflow
        
    def download_from_url(self, url: str) -> List[Path]:
        """Process 3: Download files from Internet Archive URL"""
        print(f"Process 3: Downloading from {url}")
        
        downloaded_files = []
        
        # Check if it's an archive.org details page
        if "archive.org/details/" in url:
            # Extract identifier
            match = re.search(r'archive\.org/details/([^/\s]+)', url)
            if match:
                identifier = match.group(1)
                print(f"Archive identifier: {identifier}")
                
                # Get file list from metadata API
                try:
                    metadata_url = f"https://archive.org/metadata/{identifier}/files"
                    response = requests.get(metadata_url, timeout=30)
                    if response.status_code == 200:
                        files_data = response.json()
                        for file_info in files_data.get("result", []):
                            name = file_info.get("name", "")
                            if name and self._is_downloadable(name):
                                file_url = f"https://archive.org/download/{identifier}/{name}"
                                self._download_file(file_url, name)
                                downloaded_files.append(self.download_dir / name)
                except Exception as e:
                    print(f"Error fetching metadata: {e}")
                    # Fallback to wget
                    self._wget_recursive(url)
            else:
                self._wget_recursive(url)
                
        # Check if it's a direct file URL
        elif any(url.endswith(ext) for ext in ['.zip', '.7z', '.tar', '.gz', '.tgz', '.rar', '.exe', '.iso']):
            print("Direct file URL detected")
            local_path = self.download_dir / "direct_download"
            self._download_file(url, "direct_download")
            downloaded_files.append(local_path)
            
        # General URL
        else:
            self._wget_recursive(url)
        
        # Extract archives
        self._extract_archives()
        
        # Collect all files
        all_files = list(self.download_dir.rglob("*"))
        all_files = [f for f in all_files if f.is_file()]
        
        return all_files
        
    def _is_downloadable(self, filename: str) -> bool:
        """Check if file should be downloaded"""
        downloadable_extensions = ['.zip', '.7z', '.tar', '.gz', '.tgz', '.rar', 
                                   '.exe', '.dll', '.txt', '.pdf', '.jpg', '.jpeg', 
                                   '.png', '.iso', '.bin', '.img', '.dat']
        return any(filename.lower().endswith(ext) for ext in downloadable_extensions)
        
    def _download_file(self, url: str, save_as: str):
        """Download a single file"""
        save_path = self.download_dir / save_as
        print(f"  Downloading: {url}")
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"  Saved to: {save_path}")
        except Exception as e:
            print(f"  Error downloading {url}: {e}")
            
    def _wget_recursive(self, url: str):
        """Use wget to download recursively"""
        print(f"  Using wget for: {url}")
        try:
            subprocess.run(
                ['wget', '-q', '-r', '-np', '-nH', '--cut-dirs=1', '-R', 'index.html*', url],
                cwd=self.download_dir,
                check=True
            )
        except Exception as e:
            print(f"  wget failed: {e}")
            
    def _extract_archives(self):
        """Extract all archive files"""
        print("  Extracting archives...")
        
        for archive in self.download_dir.glob("*"):
            if archive.is_file():
                ext = archive.suffix.lower()
                if ext in ['.zip', '.7z', '.tar', '.gz', '.tgz', '.rar']:
                    print(f"    Extracting: {archive.name}")
                    extract_dir = self.download_dir / f"{archive.stem}_extracted"
                    extract_dir.mkdir(exist_ok=True)
                    
                    try:
                        if ext == '.zip':
                            subprocess.run(['unzip', '-q', str(archive), '-d', str(extract_dir)], check=True)
                        elif ext == '.7z':
                            subprocess.run(['7z', 'x', str(archive), f'-o{extract_dir}', '-y'], check=True)
                        elif ext in ['.tar', '.gz', '.tgz']:
                            subprocess.run(['tar', 'xzf', str(archive), '-C', str(extract_dir)], check=True)
                        elif ext == '.rar':
                            subprocess.run(['unrar', 'x', str(archive), str(extract_dir)], check=True)
                        
                        # Remove archive after extraction
                        archive.unlink()
                        print(f"    Extracted to: {extract_dir}")
                    except Exception as e:
                        print(f"    Error extracting {archive.name}: {e}")
                        
        # Remove empty directories
        self._remove_empty_dirs()
        
    def _remove_empty_dirs(self, path: Optional[Path] = None):
        """Remove empty directories"""
        start_path = path or self.download_dir
        
        for item in start_path.iterdir():
            if item.is_dir():
                self._remove_empty_dirs(item)
                if not any(item.iterdir()):
                    item.rmdir()
                    
    def rename_files_with_paths(self) -> List[Path]:
        """Process 4: Rename files to include folder paths in filename"""
        print("Process 4: Renaming files with folder paths...")
        
        renamed_files = []
        
        # Find all files recursively
        for filepath in self.download_dir.rglob("*"):
            if filepath.is_file():
                # Get relative path from download_dir
                rel_path = filepath.relative_to(self.download_dir)
                
                # If file is at root, keep it
                if len(rel_path.parts) == 1:
                    renamed_files.append(filepath)
                    continue
                    
                # Create new filename with path
                # e.g., games/test.exe -> games/test.exe
                new_name = str(rel_path).replace('/', '/')
                new_path = self.download_dir / new_name
                
                # Move the file
                try:
                    filepath.rename(new_path)
                    print(f"  Renamed: {rel_path} -> {new_name}")
                    renamed_files.append(new_path)
                    
                    # Remove the now-empty directory
                    parent_dir = filepath.parent
                    while parent_dir != self.download_dir and not any(parent_dir.iterdir()):
                        parent_dir.rmdir()
                        parent_dir = parent_dir.parent
                        
                except Exception as e:
                    print(f"  Error renaming {rel_path}: {e}")
                    renamed_files.append(filepath)
                    
        return renamed_files
        
    def split_large_files(self, files: List[Path]) -> List[Path]:
        """Process 5: Split files larger than 1.9GB"""
        print("Process 5: Splitting large files...")
        
        result_files = []
        
        for filepath in files:
            if filepath.stat().st_size > MAX_FILE_SIZE:
                print(f"  Splitting: {filepath} ({filepath.stat().st_size / (1024*1024*1024):.2f} GB)")
                
                # Try zip split first
                try:
                    subprocess.run(
                        ['zip', '-s', f'{SPLIT_SIZE_MB}m', '-r', f'{filepath}.zip', filepath.name],
                        cwd=filepath.parent,
                        check=True
                    )
                    
                    # Check if split files were created
                    split_files = list(filepath.parent.glob(f"{filepath.name}.z*"))
                    if split_files:
                        print(f"    Split into {len(split_files)} parts using zip")
                        result_files.extend(split_files)
                        filepath.unlink()
                        continue
                except Exception as e:
                    print(f"    Zip split failed: {e}")
                    
                # Try 7z split
                try:
                    subprocess.run(
                        ['7z', 'a', '-v' + f'{SPLIT_SIZE_MB}m', f'{filepath}.7z', filepath.name],
                        cwd=filepath.parent,
                        check=True
                    )
                    
                    split_files = list(filepath.parent.glob(f"{filepath.name}.7z.*"))
                    if split_files:
                        print(f"    Split into {len(split_files)} parts using 7z")
                        result_files.extend(split_files)
                        filepath.unlink()
                        continue
                except Exception as e:
                    print(f"    7z split failed: {e}")
                    
                # If both fail, keep original
                print(f"    Could not split {filepath}, keeping original")
                result_files.append(filepath)
            else:
                result_files.append(filepath)
                
        return result_files
        
    def get_files_for_upload(self) -> List[Path]:
        """Get all files ready for upload"""
        files = list(self.download_dir.rglob("*"))
        files = [f for f in files if f.is_file()]
        return files


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python download_archive.py <url> [output_dir]")
        sys.exit(1)
        
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "download"
    
    downloader = ArchiveDownloader(output_dir)
    
    # Process 3: Download
    files = downloader.download_from_url(url)
    
    # Process 4: Rename
    renamed_files = downloader.rename_files_with_paths()
    
    # Process 5: Split
    final_files = downloader.split_large_files(renamed_files)
    
    print("\nFinal files for upload:")
    for f in final_files:
        print(f"  {f} ({f.stat().st_size / (1024*1024):.2f} MB)")
        
    print(f"\nTotal: {len(final_files)} files")


if __name__ == "__main__":
    main()
