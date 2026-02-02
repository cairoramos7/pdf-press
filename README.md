# PDF Press 📄

**PDF Press** is a modern, lightweight desktop application designed to easily compress PDF files without compromising quality. Built with Python and CustomTkinter, it provides a user-friendly drag-and-drop interface powered by the robust Ghostscript engine.

## Features

- **Drag & Drop Interface**: Simply drag your PDF files into the application window.
- **Modern UI**: Clean, dark-themed interface built with `CustomTkinter`.
- **Efficient Compression**: Uses Ghostscript (`gswin64c`) to significantly reduce file size while maintaining readability (`/ebook` quality equivalent).
- **Portable Design**: Designed to be distributed as a portable application with zero installation required (includes local Ghostscript detection).
- **Visual Feedback**: Real-time status updates during the compression process.

## Prerequisites

- **Windows OS**
- **Ghostscript**: The application requires `gswin64c.exe`. It automatically checks for:
    1. A local `gs/bin/` folder (Portable mode).
    2. A system-wide installation.

## Installation & Usage

### Running form Source

1. Clone the repository:
   ```bash
   git clone https://github.com/cairoramos7/pdf-press.git
   cd pdf-press
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

### Building the Executable

To create a standalone `.exe`, use PyInstaller:

```bash
pyinstaller --noconfirm --onedir --windowed --name "PDF Press" --add-data "<path_to_tkinterdnd2>:tkinterdnd2" app.py
```
*(Detailed build instructions coming in the distribution phase)*

## Technologies

- **Python 3**
- **CustomTkinter** (UI)
- **TkinterDnD2** (Drag functionality)
- **Ghostscript** (Compression Engine)

## License

This project is open-source. Feel free to use and modify.
