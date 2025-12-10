#  Alcohol Label Verification App

A web application that simulates the TTB (Alcohol and Tobacco Tax and Trade Bureau) label approval process. The app uses OCR technology to extract information from alcohol beverage labels and verifies that the label content matches the submitted application form.

##  Project Overview

This application was built as a take-home project for the Department of Treasury as a simple example of the types of problems we would be tackling in the Department. This was intended as a project to demonstrate full stack AI skills that can be applicable to various different projects in the future.

## Features

- **Image Upload & Preview**: Upload alcohol label images with instant preview
- **OCR Text Extraction**: Automatically extracts text from label images using Tesseract OCR
- **Smart Validation**: Compares extracted data against form inputs:
  - Brand name (fuzzy matching with 85% similarity threshold)
  - Product type/class (word-by-word matching)
  - Alcohol content (±0.3% tolerance)
  - Net contents/volume
  - Government warning statement presence
- **Detailed Results**: Clear feedback showing which fields match/mismatch and why
- **Error Handling**: Handling of invalid files, OCR failures, and edge cases

## Tech Stack

**Backend:**
- Python 3.10+
- Flask (Python web framework)
- Tesseract OCR (text extraction)
- Pillow (image processing)
- pytesseract (Python wrapper for Tesseract)

**Frontend:**
- HTML5/CSS3
- Vanilla JavaScript

## Installation

### Prerequisites

- Python 3.10 or higher
- Tesseract OCR

#### Install Tesseract:

For this README, the instruction will be for Linux distributions such as Ubuntu/ Debian. For MAC/ Windows, adjust accordingly.

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```


### Setup Instructions

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd alcohol-label-verifier
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
# Create .env file
cp .env.example .env  

# Edit .env and set:
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=1
```

5. **Run the application:**
```bash
python run.py
```

6. **Open in browser:**
```
http://localhost:5000
```

##  Testing

## Testing

Comprehensive testing instructions are available in [TESTING_GUIDE.md](TESTING_GUIDE.md).

### Quick Start

Generate test images:
```bash
python create_test_labels.py
```

This creates 10 test images covering various scenarios:
- Perfect matches (bourbon, vodka, beer, wine)
- Missing government warnings
- Various ABV levels
- Different volume formats

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed test cases and expected results.

## Project Structure
```
alcohol-label-verifier/
├── app/
│   ├── __init__.py              # App factory
│   ├── routes.py                # URL routes and request handlers
│   ├── services/
│   │   ├── ocr_service.py       # OCR text extraction logic
│   │   └── validator.py         # Validation comparison logic
│   ├── templates/
│   │   ├── index.html           # Form page
│   │   └── results.html         # Results page
│   └── static/
│       ├── css/
│       │   └── style.css        # Styling
│       └── js/
│           └── main.js          # Client-side interactions
├── uploads/                     # Temporary file storage
├── test_images/                 # Generated test images
├── config.py                    # Configuration settings
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (not in git)
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Configuration

Key settings in `config.py`:

- `SIMILARITY_THRESHOLD`: 0.85 (85% similarity for brand name matching)
- `ABV_TOLERANCE`: 0.3 (±0.3% tolerance for alcohol content)
- `MAX_CONTENT_LENGTH`: 16MB (maximum upload file size)
- `ALLOWED_EXTENSIONS`: png, jpg, jpeg, gif, webp

These setting may be adjusted in this file as needed. Will change settings for entire project.

## Deployment


## Key Design Decisions

**OCR Approach:**
- Used Tesseract OCR for reliability and ease of deployment
- Two-pass extraction (PSM 6 + PSM 11) to catch both block and scattered text
- Image preprocessing (grayscale, contrast, sharpening) for better accuracy

**Validation Strategy:**
- Fuzzy matching for brand names (handles OCR errors, case differences)
- Word-by-word matching for product types (flexible with variations)
- Tolerance-based matching for ABV (accounts for rounding, minor OCR errors)
- Substring matching for net contents (handles spacing/formatting differences)

**Error Handling:**
- Try-catch blocks at each stage
- Degradation Noted (try multiple OCR modes, fallback strategies)
- User-friendly error messages
- Auto cleanup of temporary files

## Future Enhancements

If given more time, I would add:

- **Advanced OCR**: Use ML-based OCR (Google Vision API, AWS Textract) for improved accuracy
- **Batch Processing**: Upload and verify multiple labels at once
- **PDF Support**: Handle PDF documents in addition to images
- **More Validations**: 
  - Exact government warning text matching
  - Sulfite declarations (wine)
  - Vintage year validation
  - Geographic origin verification

## Known Limitations

- OCR accuracy depends on image quality (poor lighting, blur, or low resolution may fail)
- Tesseract works best with printed text (handwritten labels not supported)
- Government warning check is basic (presence only, not exact text matching)

##  License

This project was created as a take-home assignment and is for demonstration purposes.

## Author

[Your Name]
- GitHub: [@seerreenna](https://github.com/seerreenna)
- LinkedIn: [LinkedIn](https://linkedin.com/in/serenaealvarez)

##  Acknowledgments

- TTB Guidelines: https://www.ttb.gov/
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- Flask Documentation: https://flask.palletsprojects.com/
