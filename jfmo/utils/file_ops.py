import os
import shutil
import stat
import grp
import pwd
from pathlib import Path
from ..config import Config
from .logger import Logger
from .output_formatter import OutputFormatter


class FileOps:
    """File operations class for JFMO"""
    
    @staticmethod
    def clean_name(name):
        """Clean name by removing special characters and prefixes"""
        import re
        
        # Remove extension if present
        name = os.path.splitext(name)[0]
        
        # Preserve numeric series names (like 1923)
        numeric_series_match = re.match(r'^([12][0-9]{3})\.', name)
        numeric_series_name = None
        if numeric_series_match:
            numeric_series_name = numeric_series_match.group(1)
        
        # Remove prefixes in brackets like [NOOBDL]
        name = re.sub(r'\[[^\]]*\]', '', name)
        
        # Remove suffixes like "- LostFilm.TV" or similar
        name = re.sub(r' ?- ?LostFilm\.TV.*', '', name)
        name = re.sub(r' ?- ?rus\.?.*', '', name, flags=re.IGNORECASE)
        
        # Remove alternative titles in parentheses
        name = re.sub(r' ?\([^)]+\)', '', name)
        
        # Remove season and episode patterns
        name = re.sub(r'S[0-9]{1,2}\.?E[0-9]{1,2}.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'S[0-9]{1,2}\s*\.\s*E[0-9]{1,2}.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'Season\s*[0-9]{1,2}.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[0-9]{1,2}x[0-9]{1,2}.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'Episode\s*[0-9]{1,2}.*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'E[0-9]{1,2}.*', '', name, flags=re.IGNORECASE)
        
        # Remove date patterns (YYYY.MM.DD or YYYY-MM-DD)
        name = re.sub(r'(19|20)[0-9]{2}[.\-][0-9]{1,2}[.\-][0-9]{1,2}', '', name)
        
        # Convert dots, hyphens and underscores to spaces
        name = name.replace('.', ' ').replace('_', ' ').replace('-', ' ').replace('*', '')
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove quality tags
        name = re.sub(r'\b(480|720|1080|2160|4320)p\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b(WEB|WEB-DL|WEBDL|HDR|SDR|BDRip|BluRay|x264|x265|HEVC|H264|H265)\b.*', '', name, flags=re.IGNORECASE)
        
        # Remove year at the end if it's not a numeric series title
        if numeric_series_name and not name.strip():
            return numeric_series_name
        elif numeric_series_name and name.strip() == numeric_series_name:
            return name.strip()
        else:
            name = re.sub(r'\s+(19|20)[0-9]{2}\b', '', name)
            return name.strip()
    
    @staticmethod
    def set_permissions(path, is_dir=False):
        """Set correct permissions and ownership with proper error handling"""
        if Config.TEST_MODE:
            return True
        
        if not os.path.exists(path):
            Logger.warning(f"Cannot set permissions: path does not exist: {path}")
            return False
        
        success = True
        
        try:
            # Try to set ownership using os.chown (more portable)
            try:
                uid = pwd.getpwnam(Config.MEDIA_USER).pw_uid
                gid = grp.getgrnam(Config.MEDIA_GROUP).gr_gid
                os.chown(path, uid, gid)
                Logger.debug(f"Set ownership {Config.MEDIA_USER}:{Config.MEDIA_GROUP} on {path}")
            except KeyError:
                Logger.warning(f"User/group not found: {Config.MEDIA_USER}:{Config.MEDIA_GROUP}")
                success = False
            except PermissionError:
                Logger.warning(f"Permission denied setting ownership on {path} (need root/sudo)")
                success = False
            except Exception as e:
                Logger.warning(f"Failed to set ownership on {path}: {str(e)}")
                success = False
            
            # Try to set permissions using os.chmod
            try:
                if is_dir:
                    # rwxrwxr-x for directories
                    os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
                else:
                    # rw-rw-r-- for files
                    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
                Logger.debug(f"Set permissions on {path}")
            except PermissionError:
                Logger.warning(f"Permission denied setting mode on {path}")
                success = False
            except Exception as e:
                Logger.warning(f"Failed to set permissions on {path}: {str(e)}")
                success = False
                
        except Exception as e:
            Logger.error(f"Unexpected error setting permissions on {path}: {str(e)}")
            success = False
        
        return success
    
    @staticmethod
    def ensure_dir(directory):
        """Create directory if it doesn't exist and set permissions"""
        if os.path.exists(directory):
            return True
            
        if Config.TEST_MODE:
            Logger.info(f"TEST - Would create directory: {directory}")
            return True
        
        try:
            # Create directory with parents
            Path(directory).mkdir(parents=True, exist_ok=True)
            Logger.info(f"Created directory: {directory}")
            
            # Try to set permissions (non-fatal if fails)
            FileOps.set_permissions(directory, is_dir=True)
            
            return True
            
        except PermissionError as e:
            OutputFormatter.print_file_processing_info("Error", f"Permission denied creating directory: {directory}")
            Logger.error(f"Permission denied creating directory {directory}: {str(e)}")
            return False
        except Exception as e:
            OutputFormatter.print_file_processing_info("Error", f"Failed to create directory: {str(e)}")
            Logger.error(f"Failed to create directory {directory}: {str(e)}")
            return False
    
    @staticmethod
    def move_file(source_file, dest_file):
        """Move a file and set the correct permissions"""
        # Validate source file exists
        if not os.path.exists(source_file):
            error_msg = f"Source file does not exist: {source_file}"
            OutputFormatter.print_file_processing_info("Error", error_msg)
            Logger.error(error_msg)
            return False
        
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(dest_file)
        if dest_dir and not FileOps.ensure_dir(dest_dir):
            return False
        
        # Handle test mode
        if Config.TEST_MODE:
            action_msg = f"Would move: {source_file} -> {dest_file}"
            OutputFormatter.print_file_processing_info("Test Mode", "No changes made")
            Logger.info(f"TEST - {action_msg}")
            return True
        
        # Check if destination already exists
        if os.path.exists(dest_file):
            Logger.warning(f"Destination file already exists: {dest_file}")
            # Try to remove it first
            try:
                os.remove(dest_file)
                Logger.info(f"Removed existing destination file: {dest_file}")
            except Exception as e:
                error_msg = f"Cannot remove existing destination: {str(e)}"
                OutputFormatter.print_file_processing_info("Error", error_msg)
                Logger.error(f"Cannot remove {dest_file}: {str(e)}")
                return False
        
        # Actual file move
        try:
            # Use shutil.move which handles cross-device moves
            shutil.move(source_file, dest_file)
            Logger.info(f"MOVING: {source_file} -> {dest_file} (success)")
            
            # Try to set permissions (non-fatal if fails)
            FileOps.set_permissions(dest_file, is_dir=False)
            
            return True
            
        except PermissionError as e:
            error_msg = f"Permission denied: {str(e)}"
            OutputFormatter.print_file_processing_info("Error", error_msg)
            Logger.error(f"ERROR MOVING (permission denied): {source_file} -> {dest_file} ({str(e)})")
            return False
        except shutil.Error as e:
            error_msg = f"Error moving file: {str(e)}"
            OutputFormatter.print_file_processing_info("Error", error_msg)
            Logger.error(f"ERROR MOVING (shutil error): {source_file} -> {dest_file} ({str(e)})")
            return False
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            OutputFormatter.print_file_processing_info("Error", error_msg)
            Logger.error(f"ERROR MOVING (unexpected): {source_file} -> {dest_file} ({str(e)})")
            return False
    
    @staticmethod
    def remove_empty_dir(directory):
        """Remove an empty directory"""
        if not os.path.exists(directory):
            return False
            
        if Config.TEST_MODE:
            if not os.listdir(directory):
                Logger.info(f"TEST - Would remove empty directory: {directory}")
                return True
            return False
        
        try:
            if not os.listdir(directory):
                os.rmdir(directory)
                Logger.info(f"REMOVED EMPTY DIRECTORY: {directory}")
                return True
            return False
        except PermissionError as e:
            Logger.warning(f"Permission denied removing directory {directory}: {str(e)}")
            return False
        except Exception as e:
            OutputFormatter.print_file_processing_info("Error", f"Failed to remove directory: {str(e)}")
            Logger.error(f"Failed to remove directory {directory}: {str(e)}")
            return False
    
    @staticmethod
    def is_video_file(filename):
        """Check if file is a video file based on extension"""
        return filename.lower().endswith(Config.VIDEO_EXTENSIONS)