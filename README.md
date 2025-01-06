# PicFusion

PicFusion is a simple yet powerful tool that allows you to merge multiple images vertically, horizontally, or in a grid into a single image. You can reorder the images in the list and save the final merged result

![image](https://github.com/user-attachments/assets/a3ed111f-192f-42b1-ada2-5a699d5f989f)

## Features
- **Drag-and-drop support**: Easily drag and drop images into the application.
- **Reordering**: Change the order of images before merging.
- **Vertical, horizontal, and grid merging**: Combine selected images vertically, horizontally, or in a grid layout into one.
- **Save merged image**: Save the final merged image in various formats (e.g., `.png`, `.jpg`).

## Requirements
To run this project locally, you will need the following Python packages:
- `PyQt6`
- `Pillow`

## Installation and Running Locally

1. Clone the repository:

    ```bash
    git clone https://github.com/yilmaz-mert/PicFusion.git
    cd PicFusion
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:

    ```bash
    python PicFusionApp.py
    ```

## Usage Options

### 1. Using the Precompiled Executable

For convenience, you can directly use the precompiled executable file `PicFusion.exe` provided in this repository. You can find it in the `dist` folder.

- **Steps to Use:**
  - Download the `PicFusion.exe` file.
  - Double-click to run the application.
  - No additional installation is required.

### 2. Build the Executable Yourself (Optional)

If you'd like to build the `.exe` file yourself, follow these steps:

1. Install PyInstaller:

    ```bash
    pip install pyinstaller
    ```

2. Use PyInstaller to compile the application:

    ```bash
    pyinstaller --onefile --icon=icon.ico PicFusionApp.py
    ```

3. The compiled `.exe` file will be available in the `dist` folder.

## How It Works
1. Drag and drop image files into the application, or use the **Add Images** button to select files.
2. Rearrange the images in the desired order.
3. Click the **Merge Images** button to combine the images vertically.
4. Save the merged image to your preferred location.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
