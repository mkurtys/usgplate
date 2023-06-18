import logging
import os
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from typing import Callable

logger = logging.getLogger(__name__)


class DirDirScanner(QThread):
    """
    Scans directory for new directories and emits signal when new directory is found
    """
    directory_found = Signal(str)
    file_found = Signal(str)
    def __init__(self,
                directory: str|Path,
                file_filter_fn: Callable[[str], bool]|None = None):
        super().__init__()
        self.root_directory = os.path.expanduser(str(directory))
        self.scan_interval = 1
        self.file_filter_fn = file_filter_fn

    def run(self):
        logger.info("DirDirScanner started on %s", self.root_directory)
        root_dir_subdirs = self.scan_directory_for_new_items(self.root_directory, set(), scan_for_files=False)[0]
        latest_subdirectory = None
        latest_subdirectory_files = set()
        while not self.isInterruptionRequested():
            self.sleep(self.scan_interval)

            root_dir_subdirs, root_dir_new_subdirs = self.scan_directory_for_new_items(self.root_directory, root_dir_subdirs, scan_for_files=False)
            if root_dir_new_subdirs:
                # take the last modified directory
                # do not emit all new directories since last scan
                latest_subdirectory = root_dir_new_subdirs[0] 
                logger.debug("New directory found: %s", latest_subdirectory)
                self.directory_found.emit(os.path.join(self.root_directory, latest_subdirectory))
                latest_subdirectory_new_files = set()
            if latest_subdirectory:
                try:
                    latest_subdirectory_files, latest_subdirectory_new_files = \
                        self.scan_directory_for_new_items(os.path.join(self.root_directory, latest_subdirectory),
                                                        latest_subdirectory_files, scan_for_files=True)
                    for latest_subdirectory_new_file in latest_subdirectory_new_files[::-1]:
                        logger.debug("New file found: %s", latest_subdirectory_new_file)
                        self.file_found.emit(os.path.join(self.root_directory, latest_subdirectory, latest_subdirectory_new_file))
                except FileNotFoundError:
                    # directory was removed
                    latest_subdirectory = None
                    latest_subdirectory_files = set()
        logger.info("DirDirScanner finished")

    def scan_directory_for_new_items(self, directory: str, old_items_set: set[str], scan_for_files: bool = True) -> tuple[set[str], list[str]]:
        """
        Raises:
            FileNotFoundError: if directory does not exist
        """
        if scan_for_files:
            items = { f.name:f.stat() for f in os.scandir(directory) 
                    if f.is_file() and self.file_filter_fn(f.name) }
        else:
            items = { f.name:f.stat() for f in os.scandir(directory) 
                    if f.is_dir() }
        all_dir_items_names = set(items.keys())
        items_diff = all_dir_items_names - old_items_set
        if items_diff:
            new_items_names_with_stats = ( (name,items[name]) for name in items_diff)
            new_items_names_sorted_by_mtime = [f[0] for f in
                                                sorted(new_items_names_with_stats,
                                                    key=lambda x: x[1].st_mtime, reverse=True)]
            return all_dir_items_names, new_items_names_sorted_by_mtime
        return all_dir_items_names, []


