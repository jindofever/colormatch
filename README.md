# Color Match

Korean personal color season analysis from photos of a face.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
```

## Mobile web app

```bash
.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
```

Open `http://<your-machine-ip>:8000` on your phone. Photos are taken or picked from the
camera roll, downscaled server-side before the model call, and the response is rendered
with color swatches for the recommended hex codes.

## CLI

```bash
.venv/bin/python main.py mandy1.jpg mandy2.jpg
```

With no arguments it falls back to `photo_array` in `main.py`.
