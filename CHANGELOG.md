# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Initial project structure.
- **GUI**: Modern interface using `CustomTkinter`.
- **Drag-and-Drop**: Implemented using `TkinterDnD2`.
- **Compression Logic**: Integrated Ghostscript (`gswin64c`) command for PDF compression.
- **Auto-detection**: Smart detection of Ghostscript binary (local folder or system PATH).
- **Async Processing**: Compression runs in a separate thread to keep UI responsive.
- **Git**: Repository initialization.

### Planned
- Standalone `.exe` build with PyInstaller.
- Portable package creation script.
