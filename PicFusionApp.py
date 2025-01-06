# Author: yilmaz-mert
# Version: 1.0.0
# Date: 2025-01-05

import sys
import ctypes
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QListWidget, QPushButton
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PIL import Image
from PicFusion_ui import Ui_MainWindow


def set_app_user_model_id(app_id: str):
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)


class DragDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.source() == self:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls() or event.source() == self:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    self.addItem(file_path)
        elif event.source() == self:
            super().dropEvent(event)
        else:
            event.ignore()


class ImageMergerApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('icon.ico'))

        self.image_list = self.findChild(QListWidget, 'imageListWidget')
        self.drag_drop_list = DragDropListWidget(self)
        self.drag_drop_list.setGeometry(self.image_list.geometry())
        self.drag_drop_list.setObjectName('imageListWidget')
        self.image_list.parent().layout().replaceWidget(self.image_list, self.drag_drop_list)
        self.image_list.deleteLater()
        self.image_list = self.drag_drop_list

        self.add_button = self.findChild(QPushButton, 'addButton')
        self.remove_button = self.findChild(QPushButton, 'removeButton')
        self.merge_button = self.findChild(QPushButton, 'mergeButton')

        self.add_button.clicked.connect(self.add_images)
        self.remove_button.clicked.connect(self.remove_selected_images)
        self.merge_button.clicked.connect(self.merge_and_save_images)

    def add_images(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.image_list.addItems(selected_files)

    def remove_selected_images(self):
        for item in self.image_list.selectedItems():
            self.image_list.takeItem(self.image_list.row(item))

    def merge_and_save_images(self):
        image_paths = [self.image_list.item(i).text() for i in range(self.image_list.count())]
        if not image_paths:
            return

        image_objects = [Image.open(path) for path in image_paths]

        widths, heights = zip(*(img.size for img in image_objects))
        total_height = sum(heights)
        max_width = max(widths)

        merged_image = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for img in image_objects:
            merged_image.paste(img, (0, y_offset))
            y_offset += img.height

        file_dialog = QFileDialog()
        save_path, _ = file_dialog.getSaveFileName(self, "Save Merged Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")

        if save_path:
            merged_image.save(save_path)


if __name__ == "__main__":
    set_app_user_model_id("PicFusionApp")
    app = QApplication(sys.argv)
    window = ImageMergerApp()
    window.show()
    sys.exit(app.exec())
