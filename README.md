# SnapSort

SnapSort is a Python-based  application that helps you organize your photos and videos efficiently. Using file metadata, SnapSort groups files by their recording dates and allows users to sort them into event-specific directories.

## Features

- **File Grouping by Date**: Automatically groups photos and videos by their recording dates using EXIF metadata.
- **Custom Event Organization**: Select files or groups and assign them to event directories with custom names.
- **Multi-Day Events**: Supports organizing files across multiple dates into a single event.
- **Thumbnail Previews**: Generates and displays thumbnails for photos.
- **Intuitive Web Interface**: Simple browser-based UI for selecting, previewing, and organizing files.

## Usage

1. Start the Flask application:

   ```bash
   python app.py
   ```

2. Open your browser and navigate to:

   ```
   http://127.0.0.1:5000/
   ```

3. Upload your files to the `uploads` directory.

4. Use the web interface to:

   - View files grouped by recording date.
   - Select files and organize them into event directories.
   - Assign event names and handle multi-day events.
