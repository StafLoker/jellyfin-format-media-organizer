"""
Daemon mode for JFMO - watches directories and processes files automatically
"""
import os
import time
import signal
import sys
from typing import Set
from threading import Event

from .config import Config
from .utils import Logger, FileOps, Colors, IncompleteChecker
from .__main__ import process_files, process_directories
from .detectors import SeasonEpisodeDetector


class FileWatcher:
    """Watches directory for new files and processes them"""
    
    def __init__(self, watch_dir: str, incomplete_dir: str = None, check_interval: int = 10):
        """
        Initialize file watcher
        
        Args:
            watch_dir: Directory to watch for new files
            incomplete_dir: Directory with incomplete downloads
            check_interval: Seconds between checks
        """
        self.watch_dir = watch_dir
        self.incomplete_dir = incomplete_dir
        self.check_interval = check_interval
        self.known_files: Set[str] = set()
        self.processing_files: Set[str] = set()
        self.stop_event = Event()
        
        Logger.info(f"FileWatcher initialized - watching: {watch_dir}")
        if incomplete_dir:
            Logger.info(f"Incomplete directory: {incomplete_dir}")
    
    def _scan_directory(self) -> Set[str]:
        """Scan directory and return set of all files"""
        files = set()
        try:
            for root, _, filenames in os.walk(self.watch_dir):
                for filename in filenames:
                    if FileOps.is_video_file(filename):
                        full_path = os.path.join(root, filename)
                        files.add(full_path)
        except Exception as e:
            Logger.error(f"Error scanning directory: {e}")
        return files
    
    def _is_file_stable(self, filepath: str, wait_time: int = 5) -> bool:
        """
        Check if file is stable (not being written to)
        
        Args:
            filepath: Path to file
            wait_time: Seconds to wait between size checks
            
        Returns:
            bool: True if file size hasn't changed
        """
        try:
            if not os.path.exists(filepath):
                return False
            
            size1 = os.path.getsize(filepath)
            time.sleep(wait_time)
            size2 = os.path.getsize(filepath)
            
            return size1 == size2
        except Exception as e:
            Logger.error(f"Error checking file stability: {e}")
            return False
    
    def _should_skip_series_file(self, filepath: str) -> bool:
        """
        Check if series file should be skipped due to incomplete episodes
        
        Args:
            filepath: Path to series file
            
        Returns:
            bool: True if should skip
        """
        filename = os.path.basename(filepath)
        season_episode = SeasonEpisodeDetector.detect(filename)
        
        if not season_episode:
            return False
        
        season_num, _ = season_episode
        
        # Extract series name
        from .processors import SeriesProcessor
        processor = SeriesProcessor()
        clean_title = processor.get_clean_title(filename)
        
        # Check for incomplete episodes
        if IncompleteChecker.has_incomplete_episodes(clean_title, f"{int(season_num):02d}", self.incomplete_dir):
            Logger.warning(f"Skipping {filename} - incomplete episodes exist")
            return True
        
        return False
    
    def _process_new_file(self, filepath: str):
        """
        Process a new file
        
        Args:
            filepath: Path to the new file
        """
        filename = os.path.basename(filepath)
        
        Logger.info(f"New file: {filename}")
        print(f"{filename}")
        
        # Check if file is stable
        if not self._is_file_stable(filepath):
            Logger.info(f"Waiting for file to stabilize: {filename}")
            return
        
        # Check if it's a series file that should be skipped
        if self._should_skip_series_file(filepath):
            Logger.info(f"Skipped - incomplete episodes: {filename}")
            print(f"  {Colors.YELLOW}↳ Skipped (incomplete episodes){Colors.NC}")
            return
        
        # Add to processing set
        self.processing_files.add(filepath)
        
        try:
            # Process using main processing logic
            process_files()
            process_directories()
            
            Logger.info(f"Processed: {filename}")
            print(f"  {Colors.GREEN}✓{Colors.NC}")
            
        except Exception as e:
            Logger.error(f"Error: {filename} - {e}")
            print(f"  {Colors.RED}✗ {e}{Colors.NC}")
        finally:
            # Remove from processing set
            self.processing_files.discard(filepath)
    
    def start(self):
        """Start watching directory"""
        Logger.info("File watcher started")
        
        # Initial scan
        self.known_files = self._scan_directory()
        Logger.info(f"Watching {len(self.known_files)} existing files")
        
        while not self.stop_event.is_set():
            try:
                # Scan for new files
                current_files = self._scan_directory()
                new_files = current_files - self.known_files - self.processing_files
                
                # Process new files
                for filepath in new_files:
                    if self.stop_event.is_set():
                        break
                    self._process_new_file(filepath)
                
                # Update known files
                self.known_files = current_files
                
                # Wait before next check
                self.stop_event.wait(self.check_interval)
                
            except KeyboardInterrupt:
                Logger.info("Interrupted")
                break
            except Exception as e:
                Logger.error(f"Watch loop error: {e}")
                time.sleep(self.check_interval)
        
        Logger.info("Stopped")
    
    def stop(self):
        """Stop watching"""
        self.stop_event.set()


class DaemonManager:
    """Manages daemon mode for JFMO"""
    
    def __init__(self):
        self.watcher = None
        self.running = False
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        Logger.info(f"Signal {signum}")
        print(f"\n{Colors.YELLOW}Stopping...{Colors.NC}")
        self.stop()
        sys.exit(0)
    
    def start(self, watch_dir: str = None, incomplete_dir: str = None, check_interval: int = 10):
        """
        Start daemon mode
        
        Args:
            watch_dir: Directory to watch (defaults to Config.DOWNLOADS)
            incomplete_dir: Directory for incomplete downloads
            check_interval: Seconds between checks
        """
        # Use configured downloads directory if not specified
        if not watch_dir:
            watch_dir = Config.DOWNLOADS
        
        # Validate directories
        if not os.path.exists(watch_dir):
            print(f"{Colors.RED}Error: Watch directory does not exist: {watch_dir}{Colors.NC}")
            Logger.error(f"Watch directory does not exist: {watch_dir}")
            return False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Disable interactive mode in daemon
        Config.INTERACTIVE_MODE = False
        Logger.info("Interactive mode disabled")
        
        # Create watcher
        self.watcher = FileWatcher(watch_dir, incomplete_dir, check_interval)
        self.running = True
        
        # Minimal startup message
        print(f"{Colors.GREEN}JFMO Daemon{Colors.NC}")
        print(f"Watching: {watch_dir}")
        print(f"Interval: {check_interval}s\n")
        
        # Start watching
        try:
            self.watcher.start()
        except Exception as e:
            Logger.error(f"Daemon error: {e}")
            print(f"{Colors.RED}Error: {e}{Colors.NC}")
            return False
        
        return True
    
    def stop(self):
        """Stop daemon"""
        if self.watcher:
            self.watcher.stop()
        self.running = False