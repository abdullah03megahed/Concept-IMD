import os
import csv
from datetime import datetime
import aiofiles
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

# --- Configuration ---
UPLOADS_DIR = 'uploads'
DATA_FILE = 'form_data.csv'

# Create an instance of the FastAPI application
app = FastAPI()

# Create the uploads directory if it doesn't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)

# --- CSV File Setup ---
def initialize_csv():
    """Creates the CSV file with headers if it doesn't exist."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'fullName', 'phoneNumber', 'fullAddress',
                'government', 'academicQualification', 'graduationYear',
                'laptopOwner', 'laptopModel', 'carOwner', 'carModel',
                'clubMember', 'clubName', 'coursesComments',
                'cvUploadPath', 'idUploadPath'
            ])

initialize_csv()

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serves the main index.html file."""
    async with aiofiles.open('index.html', mode='r') as f:
        content = await f.read()
    return HTMLResponse(content=content)

@app.post("/submit")
async def handle_form(
    fullName: str = Form(...),
    phoneNumber: str = Form(...),
    fullAddress: str = Form(...),
    government: str = Form(...),
    academicQualification: str = Form(...),
    graduationYear: str = Form(...),
    laptopOwner: str = Form(...),
    carOwner: str = Form(...),
    clubMember: str = Form(...),
    cvUpload: UploadFile = File(...),
    idUpload: UploadFile = File(...),
    laptopModel: str = Form(None),
    carModel: str = Form(None),
    clubName: str = Form(None),
    coursesComments: str = Form(None)
):
    """Processes the form data, saves files, and stores info in a CSV."""

    # --- Handle File Uploads ---
    # Sanitize filenames to prevent security issues and make them unique
    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")

    cv_path = os.path.join(UPLOADS_DIR, f"{timestamp_str}_{os.path.basename(cvUpload.filename)}")
    async with aiofiles.open(cv_path, 'wb') as f_out:
        content = await cvUpload.read()
        await f_out.write(content)

    id_path = os.path.join(UPLOADS_DIR, f"{timestamp_str}_{os.path.basename(idUpload.filename)}")
    async with aiofiles.open(id_path, 'wb') as f_out:
        content = await idUpload.read()
        await f_out.write(content)

    # --- Prepare Data for CSV ---
    form_data = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'fullName': fullName, 'phoneNumber': phoneNumber, 'fullAddress': fullAddress,
        'government': government, 'academicQualification': academicQualification,
        'graduationYear': graduationYear, 'laptopOwner': laptopOwner, 'laptopModel': laptopModel or 'N/A',
        'carOwner': carOwner, 'carModel': carModel or 'N/A', 'clubMember': clubMember,
        'clubName': clubName or 'N/A', 'coursesComments': coursesComments or 'N/A',
        'cvUploadPath': cv_path, 'idUploadPath': id_path
    }

    # --- Save to CSV ---
    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=form_data.keys())
        writer.writerow(form_data)

    # --- Return a success message ---
    # Note: You need to remove the JavaScript 'alert' and form reset from your index.html
    # for this redirection to work smoothly.
    return HTMLResponse(content="""
        <html>
        <head><title>Success</title>
        <style>
            body { font-family: sans-serif; text-align: center; padding: 40px; }
            h1 { color: #4CAF50; }
            p { font-size: 1.2em; }
            a { color: #0b72b9; text-decoration: none; font-weight: bold; }
        </style>
        </head>
        <body>
            <h1>Thank You!</h1>
            <p>Your information has been submitted successfully.</p>
            <a href="/">Go back to the form</a>
        </body>
        </html>
    """, status_code=200)

# Optional: If you have other static files like CSS or images in a folder
# app.mount("/static", StaticFiles(directory="static"), name="static")