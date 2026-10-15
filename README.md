# AI-Based Phishing URL and QR Code Detector System Using Machine Learning

A modular BCA academic project implementing URL text screening, QR image decoding, lexical feature extraction, classifier comparison, and a Flask dashboard. The interface uses the **Premium Dark Security SaaS** design: deep navy surfaces, subtle blue gradients, refined cards, a central scanner, and restrained cyan accents.

## Important dataset and safety note

- `data/urls_demo.csv` contains **synthetic demonstration examples**, not a genuine public phishing dataset.
- Training metrics generated from that synthetic data are **illustrative pipeline checks only**. They are not evidence of real-world phishing detection accuracy.
- No genuine public dataset is bundled in this ZIP. To avoid falsely representing synthetic examples as real data, the training script accepts a separate labelled CSV supplied by you.
- This tool only analyzes URL text features and does not visit submitted websites. Lexical patterns can miss phishing URLs and can flag legitimate URLs. A “Likely legitimate” result does **not** guarantee safety.
- Do not enter passwords, OTPs, banking information, or other sensitive data into suspicious pages based on this result. Do not deploy the Flask development server to the public internet.

## Features

1. Enter a URL and screen it with a trained scikit-learn classifier.
2. Upload a QR image (PNG/JPG/JPEG/BMP/WEBP) and decode its contents locally with OpenCV.
3. Extract lexical URL features without contacting the target website.
4. Compare Logistic Regression, Decision Tree, Random Forest, and Extra Trees.
5. Save the selected model and evaluation summary in `model/`.
6. View the model verdict, estimated model probability when available, and selected URL signals in the dashboard.
7. Use a responsive, premium dark cybersecurity dashboard.

## Project structure

```text
phishing_url_qr_detector/
├── app.py
├── train_model.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── urls_demo.csv
├── model/
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── data_utils.py
│   ├── feature_extraction.py
│   ├── predictor.py
│   └── qr_decoder.py
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/app.js
├── tests/
│   └── test_features.py
├── uploads/
│   └── .gitkeep
├── setup_and_run.bat
└── run.bat
```

`model/url_classifier.joblib` and `model/metrics.json` are generated when you train the model; they are not included as pre-generated binaries.

## Windows setup (VS Code)

### Easiest option

1. Extract the ZIP folder.
2. Open the extracted `phishing_url_qr_detector` folder in VS Code.
3. Double-click `setup_and_run.bat`, or run it from the VS Code terminal.
4. The script creates a virtual environment, installs the listed dependencies, trains the demo model, and starts Flask.
5. Open `http://127.0.0.1:5000` in Chrome or another browser.

The first dependency installation requires an internet connection and can take a few minutes. If a package fails to install, read the terminal error and install a compatible Python version (Python 3.10–3.12 recommended).

### Manual commands in VS Code terminal (Windows PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python train_model.py
python app.py
```

If PowerShell blocks virtual-environment activation, use Command Prompt and run:

```bat
.venv\Scripts\activate.bat
```

Then open `http://127.0.0.1:5000`.

## Train using your own labelled dataset

Use a dataset you have permission to use. Check its provenance, licence, collection date, label definitions, class balance, duplicate URLs, and whether train/test examples may overlap with one another.

1. Create a CSV with exactly these required column names: `url,label`.
2. Use `label=1` for phishing and `label=0` for legitimate.
3. Keep the original source and licensing notes alongside your research records.
4. Back up the demo CSV before making changes.
5. Activate your virtual environment and run:

```powershell
python train_model.py --data "data/your_labelled_urls.csv" --mode external
```

For best practice, put the external dataset in a separate file rather than overwriting `urls_demo.csv`. The evaluation uses a stratified holdout split, but that alone does not guarantee a robust evaluation. For a serious report, use an independent test set and time-aware or source-aware split where appropriate. Avoid claiming that demo metrics represent production performance.

## QR scanning notes

- Use a clear QR image with adequate contrast.
- The QR must decode to a web URL accepted by the URL validator.
- The application limits uploads to 5 MB and deletes each temporary uploaded image after processing.
- The app does not automatically visit the decoded URL.

## Evaluation output

After `python train_model.py`, inspect `model/metrics.json`. It records the run's data mode, sample counts, metrics for each classifier, the selected model, and a clear warning when the data mode is synthetic demo data.

## Troubleshooting

- **Model not trained:** run `python train_model.py` and restart `python app.py`.
- **Missing package:** activate `.venv`, then run `pip install -r requirements.txt`.
- **QR not readable:** try a higher-resolution PNG/JPG with a sharper QR code.
- **Port 5000 busy:** close the other local app using the port, or update the port in the last lines of `app.py`.
- **Dataset error:** verify the CSV has `url,label`, at least two classes, and labels represented as `1`/`0` or `phishing`/`legitimate`.
- **Unexpected results:** this model uses lexical URL patterns only; it has no reputation feed, page content inspection, or browser protection integration.

## Academic project scope

The implementation follows the stated synopsis scope: URL input, QR decoding, URL feature processing, ML prediction, and result display. Future enhancements such as larger updated datasets, testing additional classifiers, optional threat-intelligence integration, accessibility refinements, and richer QR-format errors can be developed separately.
