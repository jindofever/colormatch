import io
import os
import re

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageOps

from main import analyze_images

MAX_IMAGES = 5
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_DIMENSION = 1024
JPEG_QUALITY = 85
HEX_PATTERN = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Color Match")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def normalize_image(raw):
	"""Downscale and re-encode an uploaded photo as JPEG so phone-sized photos upload fast."""
	try:
		image = Image.open(io.BytesIO(raw))
		image = ImageOps.exif_transpose(image).convert("RGB")
	except Exception:
		raise HTTPException(status_code=400, detail="One of the photos could not be read. Try a JPEG or PNG.")

	image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
	buffer = io.BytesIO()
	image.save(buffer, format="JPEG", quality=JPEG_QUALITY)
	return buffer.getvalue()


def extract_colors(text):
	seen = []
	for match in HEX_PATTERN.findall(text):
		value = match.lower()
		if value not in seen:
			seen.append(value)
	return seen


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
	return templates.TemplateResponse(request, "index.html", {"max_images": MAX_IMAGES})


@app.get("/healthz")
def healthz():
	return {"ok": True, "openai_key_configured": bool(os.environ.get("OPENAI_API_KEY"))}


@app.post("/api/analyze")
async def analyze(photos: list[UploadFile]):
	if not photos:
		raise HTTPException(status_code=400, detail="Add at least one photo of your face.")
	if len(photos) > MAX_IMAGES:
		raise HTTPException(status_code=400, detail=f"Please upload at most {MAX_IMAGES} photos.")

	images = []
	for photo in photos:
		raw = await photo.read()
		if not raw:
			continue
		if len(raw) > MAX_UPLOAD_BYTES:
			raise HTTPException(status_code=413, detail="That photo is too large. Please pick one under 20MB.")
		images.append(normalize_image(raw))

	if not images:
		raise HTTPException(status_code=400, detail="Add at least one photo of your face.")

	if not os.environ.get("OPENAI_API_KEY"):
		raise HTTPException(status_code=503, detail="Server is missing OPENAI_API_KEY.")

	try:
		analysis = analyze_images(images)
	except Exception as exc:
		return JSONResponse(status_code=502, content={"detail": f"Analysis failed: {exc}"})

	return {"analysis": analysis, "colors": extract_colors(analysis)}
