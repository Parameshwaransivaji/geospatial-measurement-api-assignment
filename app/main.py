import sys
from pathlib import Path

# Add project root directory to sys.path so both 'app.services' and 'services' work smoothly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, UploadFile, File, HTTPException
import uuid

# Now importing relative to app module works cleanly everywhere
try:
    from app.services import process_geospatial_file
except ImportError:
    from services import process_geospatial_file

app = FastAPI(title="Geospatial File Measurement API")

db = {}

@app.post("/api/files/")
async def upload_file(file: UploadFile = File(...)):
    if not (file.filename.endswith(".zip") or file.filename.endswith(".kml")):
        raise HTTPException(status_code=400, detail="Only .zip (Shapefile) or .kml files allowed")

    file_bytes = await file.read()
    file_id = str(uuid.uuid4())[:8]

    try:
        data = process_geospatial_file(file_bytes, file.filename)
        db[file_id] = {
            "id": file_id,
            "filename": data["filename"],
            "feature_count": data["feature_count"],
            "crs": data["crs"],
            "status": "COMPLETED",
            "features": data["features"],
            "measurements": data["measurements"]
        }
        return {"id": file_id, "message": "File processed successfully", "status": "COMPLETED"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/api/files/{file_id}")
async def get_file_info(file_id: str):
    if file_id not in db:
        raise HTTPException(status_code=404, detail="File ID not found")
    
    info = db[file_id]
    return {
        "id": info["id"],
        "filename": info["filename"],
        "feature_count": info["feature_count"],
        "crs": info["crs"],
        "status": info["status"]
    }

@app.get("/api/files/{file_id}/measurements/")
async def get_measurements(file_id: str):
    if file_id not in db:
        raise HTTPException(status_code=404, detail="File ID not found")
    
    return {
        "id": file_id,
        "measurements": db[file_id]["measurements"]
    }

if __name__ == "__main__":
    import uvicorn
    # Passing 'app' object directly avoids string reloading import issues in Python 3.14
    uvicorn.run(app, host="127.0.0.1", port=8000)
