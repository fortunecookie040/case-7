from flask import Flask, request, jsonify, render_template
from datetime import datetime
from azure.storage.blob import BlobServiceClient, ContentSettings
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

## Add required imports
CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
CONTAINER_NAME = os.environ.get("IMAGES_CONTAINER", "lanternfly-images-5r7x2wsz")

bsc = BlobServiceClient.from_connection_string(CONNECTION_STRING) ## Create Blob Service Client
cc = bsc.get_container_client(CONTAINER_NAME) # Replace with Container name cc.url will get you the url path to the container.  
app = Flask(__name__)
@app.post("/api/v1/upload")
def upload():
    f = request.files["file"]
    filename = secure_filename(f.filename)
    if not filename:
        return jsonify(ok=False, error="Invalid filename"), 400
    blob = cc.get_blob_client(filename)
    blob.upload_blob(
        f.read(),
    overwrite=True,
        content_settings=ContentSettings(content_type=f.mimetype or "application/octet-stream")
    )
    return jsonify(ok=True, url=f"{cc.url}/{filename}")
   
## Add other API end points. (/api/v1/gallery)  and (/api/v1/health)\
@app.get("/api/v1/gallery")
def gallery():
    items = [{"name": b.name, "url": f"{cc.url}/{b.name}"} for b in cc.list_blobs()]
    return jsonify(ok=True, gallery=items)

@app.get("/api/v1/health")
def health():
    try:
        cc.get_container_properties()
        return jsonify(ok=True, status="ok", time=datetime.utcnow().isoformat() + "Z", container_url=cc.url)
    except Exception as e:
        return jsonify(ok=False, status="error", error=str(e)), 500

@app.get("/")
def index():
    return render_template("upload.html")

if __name__ == "__main__":
    print("Starting Flask on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)

    