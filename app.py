"""Flask entry point for the AI-based phishing URL and QR code detector.

Important: this is a screening aid, not a guarantee that a website is safe.
The bundled dataset is synthetic demo data. Do not claim real-world accuracy
until the model has been trained and tested on a suitable, independent,
genuine labelled dataset.
"""
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from src.predictor import URLPredictor
from src.qr_decoder import decode_qr_image, QRDecodeError
from src.feature_extraction import normalize_url, URLValidationError

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Limit uploads to 5 MB.
predictor = URLPredictor(BASE_DIR / "model" / "url_classifier.joblib")


def analyze(raw_url: str) -> dict:
    """Validate a URL and return the model prediction and explanatory context."""
    url = normalize_url(raw_url)
    result = predictor.predict(url)
    result["url"] = url
    result["screening_notice"] = (
        "Automated screening only. A 'likely legitimate' result is not proof of safety."
    )
    return result


@app.get("/")
def index():
    model_ready = predictor.is_ready()
    return render_template("index.html", model_ready=model_ready)


@app.post("/api/analyze")
def api_analyze():
    payload = request.get_json(silent=True) or request.form
    raw_url = str(payload.get("url", "")).strip()
    try:
        return jsonify({"ok": True, "result": analyze(raw_url)})
    except URLValidationError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except FileNotFoundError:
        return jsonify({
            "ok": False,
            "error": "The model is not trained yet. Run train_model.py, then restart the app."
        }), 503
    except Exception:
        app.logger.exception("Unexpected URL analysis failure")
        return jsonify({"ok": False, "error": "Analysis failed. Check the terminal log and try again."}), 500


@app.post("/api/scan-qr")
def api_scan_qr():
    upload = request.files.get("qr_image")
    if not upload or not upload.filename:
        return jsonify({"ok": False, "error": "Choose a QR code image first."}), 400
    suffix = Path(secure_filename(upload.filename)).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        return jsonify({"ok": False, "error": "Use a PNG, JPG, JPEG, BMP, or WEBP image."}), 400

    # Use a random server-side name and never trust the submitted filename.
    import uuid
    destination = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
    try:
        upload.save(destination)
        decoded_url = decode_qr_image(destination)
        result = analyze(decoded_url)
        return jsonify({"ok": True, "result": result, "decoded_url": decoded_url})
    except QRDecodeError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except URLValidationError as exc:
        return jsonify({"ok": False, "error": f"The QR code did not contain a valid web URL: {exc}"}), 400
    except FileNotFoundError:
        return jsonify({"ok": False, "error": "The model is not trained yet. Run train_model.py, then restart the app."}), 503
    except Exception:
        app.logger.exception("Unexpected QR scan failure")
        return jsonify({"ok": False, "error": "QR analysis failed. Check the terminal log and try again."}), 500
    finally:
        # Remove the upload after processing to avoid retaining user images.
        try:
            destination.unlink(missing_ok=True)
        except Exception:
            app.logger.warning("Could not remove a temporary QR upload")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "model_ready": predictor.is_ready(),
                    "dataset_notice": "Bundled data is synthetic demonstration data."})


if __name__ == "__main__":
    # Local development only. Do not expose Flask's development server publicly.
    app.run(host="127.0.0.1", port=5000, debug=False)
