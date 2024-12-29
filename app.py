import hashlib
import logging
import os
from collections import defaultdict

from flask import Flask, render_template, request
from PIL import ExifTags, Image

app = Flask(__name__)

BASE_DIR = "./uploads"
THUMBNAIL_DIR = "./static/thumbnails"
thumbnails_created = False

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Ensure directories exist
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

files_with_thumbnails: dict[str, str] = {}


@app.route("/")
def home():
    return render_template("index.html", files_with_thumbnails=files_with_thumbnails)


def organize():
    event_name = request.form.get("event_name")
    selected_files = request.form.getlist("files")
    if not selected_files:
        return "No files selected", 200

    # Extract dates from selected files
    dates = set()
    for file in selected_files:
        file_path = os.path.join(BASE_DIR, file)
        date = get_image_date(file_path)  # Use your date extraction function
        if date:
            dates.add(date)

    # Determine the date range
    if dates:
        sorted_dates = sorted(dates)  # Sort dates to find the range
        if len(sorted_dates) == 1:
            date_range = sorted_dates[0]
        else:
            date_range = f"{sorted_dates[0]} to {sorted_dates[-1]}"
    else:
        date_range = "Unknown-Date"

    # Create the event directory with the date range included
    event_dir = os.path.join(BASE_DIR, f"{date_range} {event_name}")

    try:
        os.makedirs(event_dir, exist_ok=True)
        for file in selected_files:
            src = os.path.join(BASE_DIR, file)
            dest = os.path.join(event_dir, file)
            os.rename(src, dest)
        return "Files organized successfully!", 200
    except Exception as e:
        app.logger.error(f"Error organizing files: {e}")
        return "Error organizing files.", 500


def delete():
    selected_files = request.form.getlist("files")
    for file in selected_files:
        try:
            src = os.path.join(BASE_DIR, file)
            os.remove(src)
        except Exception as e:
            logging.error(f"Error deleting file: {e}")
            return "Error", 500
    return "File deleted successfully", 200


@app.route("/", methods=["POST"])
def handle_action():
    action = request.form.get("action")
    if action == "organize":
        return organize()
    if action == "delete":
        return delete()


def generate_thumbnail_filename(file_path):
    """Generate a unique thumbnail filename based on file hash."""
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    file_ext = os.path.splitext(file_path)[1]  # Keep original extension
    return f"{file_hash}{file_ext}"


def get_image_date(file_path):
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    if ExifTags.TAGS.get(tag) == "DateTime":
                        return value.split()[0].replace(":", "-")  # Format: YYYY-MM-DD
    except Exception:
        pass
    return "Unknown Date"


@app.before_request
def prepare_thumbnails():
    global files_with_thumbnails
    files_with_thumbnails = defaultdict(list)

    current_files = set(os.listdir(BASE_DIR))

    for file in current_files:
        file_path = os.path.join(BASE_DIR, file)
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            date = get_image_date(file_path)
            thumbnail = generate_thumbnail_filename(file_path)
            thumbnail_path = os.path.join(THUMBNAIL_DIR, thumbnail)

            if not os.path.exists(thumbnail_path):
                with Image.open(file_path) as img:
                    img.thumbnail((150, 150))
                    img.save(thumbnail_path)

            files_with_thumbnails[date].append(
                {"thumbnail": thumbnail, "original": file}
            )
        else:
            files_with_thumbnails["Unsupported"].append(
                {"thumbnail": None, "original": file}
            )


if __name__ == "__main__":
    logging.info("Starting SnapSort...")
    app.run(debug=True)
