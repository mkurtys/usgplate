from PySide6.QtWidgets import QFileDialog


# widget to load all images from directory
def choose_directory_modal(start_directory = "."):
    # open file dialog
    file_dialog = QFileDialog()
    # set file dialog to open directory
    file_dialog.setFileMode(QFileDialog.Directory)
    # set file dialog to open in current directory
    file_dialog.setDirectory(start_directory)
    # set file dialog to open
    if file_dialog.exec():
        # get selected directory
        directory = file_dialog.selectedFiles()[0]
        return directory
    
    return None
