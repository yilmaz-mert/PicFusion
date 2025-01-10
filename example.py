"""
 This code is under development.

 This script is part of the PicFusion project and is currently a work in progress.
 The primary objective of this code is to provide a graphical user interface (GUI)
for managing and merging images using PyQt6.

 The application allows users to:
 - Drag and drop images into a grid layout.
 - Select, move, and remove images within the grid.
 - Merge selected images into a single image and save the result.

 Please note that this script is not yet complete and may contain bugs or incomplete
features. The development process is ongoing, and the code will be updated frequently.

 If you encounter any issues or have suggestions for improvements, please feel free to
contribute to the project or report issues on the project's GitHub repository.

 Thank you for your understanding and support as we continue to develop and improve
this application.
"""

from PyQt6.QtWidgets import QMessageBox, QApplication, QMainWindow, QFileDialog, QGridLayout, QWidget, QLabel
from PyQt6.QtGui import QPixmap, QDrag, QPainter
from PyQt6.QtCore import Qt, QMimeData
import os
import sys
import math

# Import the converted UI Python file
from example_ui import Ui_MainWindow


class DraggableLabel(QLabel):
    def __init__(self, pixmap, filename):
        super().__init__()
        self.drag_start_position = None
        self.original_pixmap = pixmap
        self.setPixmap(pixmap)
        self.setToolTip(filename)
        self.setScaledContents(True)
        self.setMinimumSize(100, 100)
        self.selected = False
        self.dragging = False

        self.selection_overlay = QLabel(self)
        self.selection_overlay.setStyleSheet("""
            background-color: rgba(0, 123, 255, 0.3);
            border: 2px solid #007BFF;
        """)
        self.selection_overlay.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
            self.dragging = False

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            distance = (event.pos() - self.drag_start_position).manhattanLength()
            if distance >= QApplication.startDragDistance():
                self.dragging = True  
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setImageData(self.pixmap().toImage())
                drag.setMimeData(mime_data)
                drag.setPixmap(self.pixmap())
                drag.setHotSpot(event.pos() - self.rect().topLeft())
                drag.exec(Qt.DropAction.MoveAction)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.dragging:
            self.selected = not self.selected
            self.update_selection_border()

    def update_selection_border(self):
        if self.selected:
            self.selection_overlay.setGeometry(0, 0, self.width(), self.height())
            self.selection_overlay.show()
        else:
            self.selection_overlay.hide()

    def resize_pixmap(self, width, height):
        self.setPixmap(self.original_pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio))
        self.selection_overlay.setGeometry(0, 0, width, height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.selection_overlay.setGeometry(0, 0, self.width(), self.height())


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.setAcceptDrops(True)
        self.setLayout(self.layout)
        self.labels = []
        self.rows = 1
        self.cols = 1
        self.parent = parent

    def addImage(self, pixmap, filename):
        label = DraggableLabel(pixmap, filename)
        self.layout.addWidget(label, (len(self.labels) // self.cols), (len(self.labels) % self.cols))
        self.labels.append(label)
        self.updateGridDimensions()

    def removeSelectedImages(self):
        selected_labels = [label for label in self.labels if label.selected]
        for label in selected_labels:
            self.layout.removeWidget(label)
            label.deleteLater()
            self.labels.remove(label)
        self.updateGridDimensions()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasImage():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path) and file_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
                    pixmap = QPixmap(file_path)
                    filename = os.path.basename(file_path)
                    self.addImage(pixmap, filename)

            self.parent.ui.RowspinBox.setEnabled(True)
            self.parent.ui.ColumnspinBox.setEnabled(True)
            self.updateSpinboxes()
            event.acceptProposedAction()

        elif event.mimeData().hasImage():
            position = event.position().toPoint()
            widget = self.childAt(position)
            if widget and isinstance(widget, DraggableLabel):
                row, col, _, _ = self.layout.getItemPosition(self.layout.indexOf(widget))
                source = event.source()
                if isinstance(source, DraggableLabel):
                    source_row, source_col, _, _ = self.layout.getItemPosition(self.layout.indexOf(source))
                    # Swap the positions of the source and target labels
                    self.layout.removeWidget(source)
                    self.layout.removeWidget(widget)
                    self.layout.addWidget(source, row, col)
                    self.layout.addWidget(widget, source_row, source_col)
                    event.setDropAction(Qt.DropAction.MoveAction)
                    event.accept()
                else:
                    event.ignore()
            else:
                event.ignore()

    def update_grid(self):
        if not self.labels:
            return
        grid_width = self.width() // self.cols
        grid_height = self.height() // self.rows
        for label in self.labels:
            label.resize_pixmap(grid_width, grid_height)

    def set_rows(self, rows):
        self.rows = rows
        self.updateGridDimensions(row_spinbox_value=rows)

    def set_cols(self, cols):
        self.cols = cols
        self.updateGridDimensions(column_spinbox_value=cols)

    def updateSpinboxes(self):
        count = len(self.labels)
        self.parent.ui.RowspinBox.setMaximum(count)
        self.parent.ui.ColumnspinBox.setMaximum(count)
        self.updateGridDimensions()

    def updateGridDimensions(self, row_spinbox_value=None, column_spinbox_value=None):
        count = len(self.labels)
        if count > 0:
            # Remove all widgets from the layout
            for i in reversed(range(self.layout.count())):
                widget = self.layout.itemAt(i).widget()
                if widget is not None:
                    self.layout.removeWidget(widget)
                    widget.setParent(None)

            if row_spinbox_value is not None:
                self.rows = row_spinbox_value
                self.cols = math.ceil(count / self.rows)
                self.parent.ui.ColumnspinBox.blockSignals(True)
                self.parent.ui.ColumnspinBox.setValue(self.cols)
                self.parent.ui.ColumnspinBox.blockSignals(False)

                for index, label in enumerate(self.labels):
                    col = index // self.rows
                    row = index % self.rows
                    self.layout.addWidget(label, row, col)

            elif column_spinbox_value is not None:
                self.cols = column_spinbox_value
                self.rows = math.ceil(count / self.cols)
                self.parent.ui.RowspinBox.blockSignals(True)
                self.parent.ui.RowspinBox.setValue(self.rows)
                self.parent.ui.RowspinBox.blockSignals(False)

                for index, label in enumerate(self.labels):
                    row = index // self.cols
                    col = index % self.cols
                    self.layout.addWidget(label, row, col)

            else:
                self.rows = self.cols = int(math.ceil(math.sqrt(count)))
                self.parent.ui.RowspinBox.blockSignals(True)
                self.parent.ui.ColumnspinBox.blockSignals(True)
                self.parent.ui.RowspinBox.setValue(self.rows)
                self.parent.ui.ColumnspinBox.setValue(self.cols)
                self.parent.ui.RowspinBox.blockSignals(False)
                self.parent.ui.ColumnspinBox.blockSignals(False)

                for index, label in enumerate(self.labels):
                    row = index // self.cols
                    col = index % self.cols
                    self.layout.addWidget(label, row, col)

            self.update_grid()
            return self.rows, self.cols
        return 1, 1

    def mergeImages(self):
        if not self.labels:
            QMessageBox.warning(self, "Warning", "No images to merge")
            return

        images = [label.original_pixmap.toImage() for label in self.labels]
        if not images:
            QMessageBox.warning(self, "Warning", "No valid images found")
            return

        try:
            if self.parent.ui.ResizeImagecheckBox.isChecked():
                # Tüm görüntüleri minimum boyuta getirmek için minimum genişlik ve yükseklik belirlenir
                min_width = min(image.width() for image in images)
                min_height = min(image.height() for image in images)
                # Görsellerin yeniden boyutlandırılması, her görüntüyü minimum boyutlara tam sığacak şekilde
                resized_images = [
                    image.scaled(min_width, min_height, Qt.AspectRatioMode.IgnoreAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
                    for image in images
                ]
            else:
                min_width = images[0].width()
                min_height = images[0].height()
                resized_images = images

            print(f"Image dimensions: width={min_width}, height={min_height}, cols={self.cols}, rows={self.rows}")

            merged_image = QPixmap(min_width * self.cols, min_height * self.rows)
            merged_image.fill(Qt.GlobalColor.transparent)

            painter = QPainter(merged_image)
            for index, image in enumerate(resized_images):
                row = index // self.cols
                col = index % self.cols
                print(f"Drawing image at row={row}, col={col}, x={col * min_width}, y={row * min_height}")
                painter.drawImage(col * min_width, row * min_height, image)
            painter.end()

            # Save the merged image with a user-defined filename and format
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Merged Image", "",
                                                       "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)")

            if file_path:
                file_extension = os.path.splitext(file_path)[1].lower()
                if file_extension not in ['.png', '.jpg', '.jpeg']:
                    QMessageBox.critical(self, "Error", "Unsupported file format. Please use .png or .jpg")
                    return

                merged_image.save(file_path)
                QMessageBox.information(self, "Success", f"Merged image saved as {file_path}")
            else:
                QMessageBox.information(self, "Cancelled", "Save operation cancelled")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.grid_widget = GridWidget(parent=self)
        self.ui.MaingridLayout.addWidget(self.grid_widget)

        self.ui.AddImagesButton.clicked.connect(self.add_images)
        self.ui.RemoveButton.clicked.connect(self.remove_images)
        self.ui.MergeButton.clicked.connect(self.merge_images)
        self.ui.RowspinBox.valueChanged.connect(self.update_rows)
        self.ui.ColumnspinBox.valueChanged.connect(self.update_cols)
        self.ui.RowspinBox.setEnabled(False)
        self.ui.ColumnspinBox.setEnabled(False)
        self.ui.VerticallycheckBox.stateChanged.connect(self.vertical_layout)
        self.ui.HorizontallycheckBox.stateChanged.connect(self.horizontal_layout)

    def update_rows(self, value):
        self.grid_widget.set_rows(value)
        self.grid_widget.updateGridDimensions(row_spinbox_value=value)

    def update_cols(self, value):
        self.grid_widget.set_cols(value)
        self.grid_widget.updateGridDimensions(column_spinbox_value=value)

    def add_images(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_dialog.exec():
            image_paths = file_dialog.selectedFiles()

            for path in image_paths:
                pixmap = QPixmap(path)
                filename = os.path.basename(path)
                self.grid_widget.addImage(pixmap, filename)

            self.ui.RowspinBox.setEnabled(True)
            self.ui.ColumnspinBox.setEnabled(True)
            self.grid_widget.updateSpinboxes()

    def remove_images(self):
        self.grid_widget.removeSelectedImages()

    def merge_images(self):
        self.grid_widget.mergeImages()

    def vertical_layout(self, state):
        if state == Qt.CheckState.Checked.value:
            self.ui.HorizontallycheckBox.blockSignals(True)
            self.ui.HorizontallycheckBox.setChecked(False)
            self.ui.HorizontallycheckBox.blockSignals(False)
            self.ui.RowspinBox.setValue(len(self.grid_widget.labels))
            self.ui.ColumnspinBox.setValue(1)
            self.ui.RowspinBox.setEnabled(False)
            self.ui.ColumnspinBox.setEnabled(False)
        else:
            self.ui.RowspinBox.setEnabled(True)
            self.ui.ColumnspinBox.setEnabled(True)

    def horizontal_layout(self, state):
        if state == Qt.CheckState.Checked.value:
            self.ui.VerticallycheckBox.blockSignals(True)
            self.ui.VerticallycheckBox.setChecked(False)
            self.ui.VerticallycheckBox.blockSignals(False)
            self.ui.RowspinBox.setValue(1)
            self.ui.ColumnspinBox.setValue(len(self.grid_widget.labels))
            self.ui.RowspinBox.setEnabled(False)
            self.ui.ColumnspinBox.setEnabled(False)
        else:
            self.ui.RowspinBox.setEnabled(True)
            self.ui.ColumnspinBox.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
