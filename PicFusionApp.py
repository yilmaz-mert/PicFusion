# Author: yilmaz-mert
# Version: 1.1.6
# Date: 2025-01-06

"""
This is a simple image merger application that allows users to merge multiple images into a single image.
The user can select multiple images from their file system, choose the layout type (vertical, horizontal, or grid),
and resize the images to the smallest dimensions before merging.
The merged image can be saved to the file system.

Python 3.12.3
PyQt6 6.8.0
Pillow 11.1.0
PyInstaller 6.11.1
"""

import sys
import ctypes
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QListWidget, QListWidgetItem, QPushButton, QToolTip, QMessageBox, QVBoxLayout, QComboBox, QCheckBox
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QEvent, QSize
from PIL import Image
from PicFusion_ui import Ui_MainWindow


def set_app_user_model_id(app_id: str):
    # Set the App User Model ID for the application
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)


ICON_SIZE = QSize(100, 100)
SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.bmp')


class DragDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.setIconSize(ICON_SIZE)

    def dragEnterEvent(self, event):
        # Accept the drag event if it contains URLs or if the source is the same list widget
        if event.mimeData().hasUrls() or event.source() == self:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        # Accept the drag move event if it contains URLs or if the source is the same list widget
        if event.mimeData().hasUrls() or event.source() == self:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # Handle the drop event to add images to the list
        if event.mimeData().hasUrls():
            event.accept()
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith(SUPPORTED_FORMATS):
                    self.add_image_item(file_path)
        elif event.source() == self:
            super().dropEvent(event)
        else:
            event.ignore()

    def add_image_item(self, file_path):
        # Add an image item to the list widget
        try:
            pixmap = QPixmap(file_path)
            icon = QIcon(pixmap.scaled(ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio))
            file_name = file_path.split('/')[-1]
            item = QListWidgetItem(icon, file_name)
            item.setToolTip(file_path)
            self.addItem(item)
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")

    def event(self, event):
        # Show tooltip when hovering over an item
        if event.type() == QEvent.Type.ToolTip:
            item = self.itemAt(event.pos())
            if item:
                QToolTip.showText(event.globalPos(), item.toolTip())
            else:
                QToolTip.hideText()
            return True
        return super().event(event)


class ImageMergerApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('icon.ico'))  # Set window icon

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

        self.add_button.setToolTip('Click to add images to the list.')
        self.remove_button.setToolTip('Click to remove selected images from the list.')
        self.merge_button.setToolTip('Click to merge selected images.')

        self.layout_combo_box = self.findChild(QComboBox, 'comboBox')

        self.layout_combo_box.setToolTip('Select the layout type for merging images.')

        self.resize_checkbox = self.findChild(QCheckBox, 'ResizecheckBox')

        self.resize_checkbox.setToolTip('Check to resize images to the smallest dimensions among them before merging.')

        self.add_button.clicked.connect(self.add_images)
        self.remove_button.clicked.connect(self.remove_selected_images)
        self.merge_button.clicked.connect(self.merge_and_save_images)

        self.current_layout = QVBoxLayout()
        self.image_list.setLayout(self.current_layout)

    def add_image_item(self, file_path):
        # Add an image item to the list widget
        self.drag_drop_list.add_image_item(file_path)

    def add_images(self):
        # Open a file dialog to select images
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                self.add_image_item(file_path)

    def remove_selected_images(self):
        # Remove selected images from the list
        for item in self.image_list.selectedItems():
            self.image_list.takeItem(self.image_list.row(item))

    @staticmethod
    def clear_layout(layout):
        # Clear the layout by removing all widgets
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)

    def merge_and_save_images(self):
        # Merge and save selected images
        image_paths = [self.image_list.item(i).toolTip() for i in range(self.image_list.count())]
        if not image_paths:
            QMessageBox.warning(self, "Warning", "No images selected to merge.")
            return

        try:
            image_objects = [Image.open(path) for path in image_paths]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open images: {e}")
            return

        if self.resize_checkbox.isChecked():
            min_width = min(img.width for img in image_objects)
            min_height = min(img.height for img in image_objects)
            image_objects = [img.resize((min_width, min_height), Image.Resampling.LANCZOS) for img in image_objects]

        merged_image = None

        selected_layout = self.layout_combo_box.currentText()

        if selected_layout == 'Vertical':
            total_width = max(img.width for img in image_objects)
            total_height = sum(img.height for img in image_objects)
            merged_image = Image.new('RGB', (total_width, total_height))
            y_offset = 0
            for img in image_objects:
                merged_image.paste(img, (0, y_offset))
                y_offset += img.height
        elif selected_layout == 'Horizontal':
            total_width = sum(img.width for img in image_objects)
            total_height = max(img.height for img in image_objects)
            merged_image = Image.new('RGB', (total_width, total_height))
            x_offset = 0
            for img in image_objects:
                merged_image.paste(img, (x_offset, 0))
                x_offset += img.width
        elif selected_layout == 'Grid':
            import math
            grid_size = math.ceil(math.sqrt(len(image_objects)))
            max_width = max(img.width for img in image_objects)
            max_height = max(img.height for img in image_objects)
            total_width = max_width * grid_size
            total_height = max_height * grid_size
            merged_image = Image.new('RGB', (total_width, total_height))
            for idx, img in enumerate(image_objects):
                x_offset = (idx % grid_size) * max_width
                y_offset = (idx // grid_size) * max_height
                merged_image.paste(img, (x_offset, y_offset))

        if merged_image:
            file_dialog = QFileDialog()
            save_path, _ = file_dialog.getSaveFileName(self, "Save Merged Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")

            if save_path:
                merged_image.save(save_path)
                QMessageBox.information(self, "Completed", "The merged image has been successfully saved.")
            else:
                QMessageBox.warning(self, "Warning", "Save operation was cancelled.")
        else:
            QMessageBox.critical(self, "Error", "Failed to merge images.")


if __name__ == "__main__":
    set_app_user_model_id("PicFusionApp")
    app = QApplication(sys.argv)
    window = ImageMergerApp()
    window.show()
    sys.exit(app.exec())
