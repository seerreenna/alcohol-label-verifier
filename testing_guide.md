# Testing Guide for Alcohol Label Verification App

This guide provides comprehensive testing instructions for the TTB Label Verification application, including testing both locally and on the live demo.

## Table of Contents

1. [Quick Start with Test Images](#quick-start-with-test-images)
2. [Testing the Live Demo](#testing-the-live-demo)
3. [Local Testing Setup](#local-testing-setup)
4. [Test Scenarios](#test-scenarios)
5. [Expected Results](#expected-results)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start with Test Images

This repository includes 10 ready-to-use test images in the [`test_images/`](test_images/) directory. Each image is designed to test specific scenarios.

### Available Test Images
```
test_images/
├── 01_bourbon_perfect_match.png       # All fields correct - spirits
├── 02_vodka_perfect_match.png         # All fields correct - vodka
├── 03_gin_missing_warning.png         # Missing government warning
├── 04_beer_ipa.png                    # Beer label - lower ABV
├── 05_wine_cabernet.png               # Wine label
├── 06_rum_spiced.png                  # Rum label - high ABV
├── 07_long_brand_name.png             # Tests text wrapping
├── 08_complex_product.png             # Complex product type
├── 09_beer_light.png                  # Low ABV beer
└── 10_whiskey_cask_strength.png       # High ABV spirit (60%)
```

## Testing the Live Demo

### Method 1: Use Repository Test Images

**No local setup required!**

1. **Navigate to [`test_images/`](test_images/) in this repository**
2. **Download a test image** (e.g., `01_bourbon_perfect_match.png`)
3. **Go to the [live demo](https://your-app.up.railway.app)**
4. **Upload the downloaded image**
5. **Fill in the form with matching data** (see [Test Scenarios](#test-scenarios) below)
6. **Click "Verify Label"** and see the results!

### Quick Test Example

**Image:** [`01_bourbon_perfect_match.png`](test_images/01_bourbon_perfect_match.png)

**Form Data:**
```
Brand Name: Old Tom Distillery
Product Class/Type: Kentucky Straight Bourbon Whiskey
Alcohol Content: 45
Net Contents: 750 mL
```
**Expected Result:** ✅ All fields pass

## Local Testing Setup

### Prerequisites

For local testing, ensure you have:

1. **Python 3.10 or higher**
2. **Tesseract OCR installed**
3. **Application dependencies installed**

### Setup Steps
```bash
# Clone the repository
git clone https://github.com/seerreenna/alcohol-label-verifier.git
cd alcohol-label-verifier

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the application
python run.py
```

Open browser to: `http://localhost:5000`

### Generate Fresh Test Images (Optional)

If you want to regenerate test images locally:
```bash
python create_test_labels.py
```

This creates/updates all test images in the `test_images/` directory.

---

## Test Scenarios

### Test 1: Perfect Match - Bourbon ✅

**Purpose:** Verify all validations pass when data matches perfectly

**Image:** `test_images/01_bourbon_perfect_match.png`

**Form Inputs:**
```
Brand Name: Old Tom Distillery
Product Class/Type: Kentucky Straight Bourbon Whiskey
Alcohol Content: 45
Net Contents: 750 mL
```

**Expected Result:** ✅ ALL PASS
- Brand Name: ✅ Matched
- Product Type: ✅ Found on label
- Alcohol Content: ✅ 45.0% matches
- Net Contents: ✅ 750 mL matches
- Government Warning: ✅ Found on label

---

### Test 2: Perfect Match - Vodka ✅

**Purpose:** Test with different beverage type

**Image:** `test_images/02_vodka_perfect_match.png`

**Form Inputs:**
```
Brand Name: Crystal Clear Vodka
Product Class/Type: Premium Vodka
Alcohol Content: 40
Net Contents: 1 L
```

**Expected Result:** ✅ ALL PASS

---

### Test 3: Missing Government Warning ❌

**Purpose:** Verify detection of missing mandatory warning

**Image:** `test_images/03_gin_missing_warning.png`

**Form Inputs:**
```
Brand Name: Rebel Spirits
Product Class/Type: Craft Gin
Alcohol Content: 42
Net Contents: 750 mL
```

**Expected Result:** ❌ FAIL (Government Warning Only)
- Brand Name: ✅ Pass
- Product Type: ✅ Pass
- Alcohol Content: ✅ Pass
- Net Contents: ✅ Pass
- Government Warning: ❌ FAIL - "Government warning statement not detected on label (required by TTB regulations)"

---

### Test 4: Brand Name Mismatch ❌

**Purpose:** Test brand name validation

**Image:** `test_images/01_bourbon_perfect_match.png`

**Form Inputs:**
```
Brand Name: Wrong Brand Name  ← INTENTIONALLY WRONG
Product Class/Type: Kentucky Straight Bourbon Whiskey
Alcohol Content: 45
Net Contents: 750 mL
```

**Expected Result:** ❌ FAIL (Brand Name)
- Brand Name: ❌ FAIL - Mismatch detected
- Product Type: ✅ Pass
- Alcohol Content: ✅ Pass
- Net Contents: ✅ Pass
- Government Warning: ✅ Pass

---

### Test 5: Product Type Mismatch ❌

**Purpose:** Test product type validation

**Image:** `test_images/01_bourbon_perfect_match.png`

**Form Inputs:**
```
Brand Name: Old Tom Distillery
Product Class/Type: Tequila  ← WRONG (label says Bourbon)
Alcohol Content: 45
Net Contents: 750 mL
```

**Expected Result:** ❌ FAIL (Product Type)
- Brand Name: ✅ Pass
- Product Type: ❌ FAIL - "Product type 'Tequila' not found on label"
- Alcohol Content: ✅ Pass
- Net Contents: ✅ Pass
- Government Warning: ✅ Pass

---

### Test 6: Alcohol Content Mismatch (Outside Tolerance) ❌

**Purpose:** Test ABV validation with significant difference

**Image:** `test_images/01_bourbon_perfect_match.png`

**Form Inputs:**
```
Brand Name: Old Tom Distillery
Product Class/Type: Kentucky Straight Bourbon Whiskey
Alcohol Content: 40  ← WRONG (label says 45%, difference = 5%)
Net Contents: 750 mL
```

**Expected Result:** ❌ FAIL (Alcohol Content)
- Brand Name: ✅ Pass
- Product Type: ✅ Pass
- Alcohol Content: ❌ FAIL - "Alcohol content mismatch: Form says 40.0%, label shows 45.0%"
- Net Contents: ✅ Pass
- Government Warning: ✅ Pass

---

### Test 7: Alcohol Content Within Tolerance ✅

**Purpose:** Test that small ABV differences are accepted

**Image:** `test_images/01_bourbon_perfect_match.png`

**Form Inputs:**
```
Brand Name: Old Tom Distillery
Product Class/Type: Kentucky Straight Bourbon Whiskey
Alcohol Content: 45.3  ← Slightly different (within ±0.3% tolerance)
Net Contents: 750 mL
```

**Expected Result:** ✅ ALL PASS
- Alcohol Content: ✅ "Alcohol content matches: 45.3% (form) ≈ 45.0% (label)"

**Note:** Tolerance is ±0.3%, so 44.7% to 45.3% would all pass

---

### Test 8: Net Contents Mismatch ❌

**Purpose:** Test volume validation

**Image:** `test_images/01_bourbon_perfect_match.png`

**Form Inputs:**
```
Brand Name: Old Tom Distillery
Product Class/Type: Kentucky Straight Bourbon Whiskey
Alcohol Content: 45
Net Contents: 1 L  ← WRONG (label says 750 mL)
```

**Expected Result:** ❌ FAIL (Net Contents)
- Brand Name: ✅ Pass
- Product Type: ✅ Pass
- Alcohol Content: ✅ Pass
- Net Contents: ❌ FAIL - "Net contents mismatch: Form says '1 L', label shows '750 mL'"
- Government Warning: ✅ Pass

---

### Test 9: Case Insensitivity ✅

**Purpose:** Verify case doesn't matter in matching

**Image:** `test_images/01_bourbon_perfect_match.png`

**Form Inputs:**
```
Brand Name: old tom distillery  ← all lowercase
Product Class/Type: KENTUCKY STRAIGHT BOURBON WHISKEY  ← all uppercase
Alcohol Content: 45
Net Contents: 750 ML  ← uppercase
```

**Expected Result:** ✅ ALL PASS
- All fields should match despite case differences

---

### Test 10: Multiple Mismatches ❌

**Purpose:** Verify all errors are reported, not just the first one

**Image:** `test_images/01_bourbon_perfect_match.png`

**Form Inputs:**
```
Brand Name: Wrong Brand
Product Class/Type: Wrong Type
Alcohol Content: 30
Net Contents: 2 L
```

**Expected Result:** ❌ FAIL (Multiple Fields)
- Brand Name: ❌ Mismatch
- Product Type: ❌ Not found
- Alcohol Content: ❌ Mismatch
- Net Contents: ❌ Mismatch
- Government Warning: ✅ Pass

**Important:** All errors should be shown, not just the first one

---

### Test 11: Beer Label (Low ABV) ✅

**Purpose:** Test with low alcohol content beverage

**Image:** `test_images/04_beer_ipa.png`

**Form Inputs:**
```
Brand Name: Hoppy Hills Brewery
Product Class/Type: India Pale Ale
Alcohol Content: 6.5
Net Contents: 12 fl oz
```

**Expected Result:** ✅ ALL PASS

---

### Test 12: Wine Label ✅

**Purpose:** Test wine-specific validation

**Image:** `test_images/05_wine_cabernet.png`

**Form Inputs:**
```
Brand Name: Sunset Vineyards
Product Class/Type: Cabernet Sauvignon
Alcohol Content: 13.5
Net Contents: 750 mL
```

**Expected Result:** ✅ ALL PASS

---

### Test 13: High ABV Spirit ✅

**Purpose:** Test with high alcohol content

**Image:** `test_images/10_whiskey_cask_strength.png`

**Form Inputs:**
```
Brand Name: Barrel House Spirits
Product Class/Type: Cask Strength Rye Whiskey
Alcohol Content: 60
Net Contents: 750 mL
```

**Expected Result:** ✅ ALL PASS

---

### Test 14: Long Brand Name ✅

**Purpose:** Test handling of long brand names

**Image:** `test_images/07_long_brand_name.png`

**Form Inputs:**
```
Brand Name: Toms Old Distillery Premium Spirits Company
Product Class/Type: Small Batch Tennessee Whiskey
Alcohol Content: 43
Net Contents: 750 mL
```

**Expected Result:** ✅ ALL PASS
- Tests text wrapping and long name extraction

---

### Test 15: Complex Product Type ✅

**Purpose:** Test handling of complex, multi-word product types

**Image:** `test_images/08_complex_product.png`

**Form Inputs:**
```
Brand Name: Heritage Distillers
Product Class/Type: Single Barrel Aged Kentucky Straight Bourbon Whiskey
Alcohol Content: 50
Net Contents: 750 mL
```

**Expected Result:** ✅ ALL PASS
- Tests word-by-word matching for complex types

---

### Test 16: Invalid File Type ⚠️

**Purpose:** Test error handling for non-image files

**Steps:**
1. Create a text file: `echo "test" > test.txt`
2. Fill form with any valid data
3. Try to upload `test.txt`

**Expected Result:** ⚠️ ERROR
- Error message: "Invalid file type. Please upload PNG, JPG, or JPEG."

---

## Expected Results Summary

### Success Indicators (✅)
- Green background on results page
- Message: "Label Verified Successfully"
- All fields show green checkmarks
- Clear confirmation messages for each field

### Failure Indicators (❌)
- Red/pink background on results page
- Message: "Label Verification Failed"
- Failed fields show red X marks
- Specific error messages explaining what didn't match

### Error Indicators (⚠️)
- Pink error banner
- Clear explanation of the problem
- Suggestion for how to fix it

---

## All Test Images Reference Table

Quick reference for all available test images:

| # | Image File | Brand Name | Product Type | ABV | Volume | Expected |
|---|------------|------------|--------------|-----|--------|----------|
| 1 | `01_bourbon_perfect_match.png` | Old Tom Distillery | Kentucky Straight Bourbon Whiskey | 45 | 750 mL | ✅ Pass |
| 2 | `02_vodka_perfect_match.png` | Crystal Clear Vodka | Premium Vodka | 40 | 1 L | ✅ Pass |
| 3 | `03_gin_missing_warning.png` | Rebel Spirits | Craft Gin | 42 | 750 mL | ❌ No warning |
| 4 | `04_beer_ipa.png` | Hoppy Hills Brewery | India Pale Ale | 6.5 | 12 fl oz | ✅ Pass |
| 5 | `05_wine_cabernet.png` | Sunset Vineyards | Cabernet Sauvignon | 13.5 | 750 mL | ✅ Pass |
| 6 | `06_rum_spiced.png` | Caribbean Gold | Spiced Rum | 47.5 | 1 L | ✅ Pass |
| 7 | `07_long_brand_name.png` | Toms Old Distillery Premium Spirits Company | Small Batch Tennessee Whiskey | 43 | 750 mL | ✅ Pass |
| 8 | `08_complex_product.png` | Heritage Distillers | Single Barrel Aged Kentucky Straight Bourbon Whiskey | 50 | 750 mL | ✅ Pass |
| 9 | `09_beer_light.png` | Mountain Brew Co | Light Lager | 4.2 | 12 fl oz | ✅ Pass |
| 10 | `10_whiskey_cask_strength.png` | Barrel House Spirits | Cask Strength Rye Whiskey | 60 | 750 mL | ✅ Pass |

---

## Troubleshooting

### OCR Returns No Text

**Symptoms:**
- Error: "Could not read text from label image"
- Error: "No text detected in image"

**Solutions:**
1. Check image quality - ensure it's clear and high resolution
2. **Local testing:** Verify Tesseract is installed: `tesseract --version`
3. **Live demo:** Try a different test image - some may work better than others
4. Check terminal logs for detailed error messages (local only)
5. **Local testing:** Try regenerating test images: `python create_test_labels.py`

---

### Brand Name Not Detected

**Symptoms:**
- Brand name validation fails even with correct input
- Error: "Could not find brand name on label"

**Solutions:**
1. **Local testing:** Check terminal logs for "Extracted brand name"
2. Try entering the brand name exactly as shown in the [reference table](#all-test-images-reference-table)
3. **Local testing:** If OCR text shows the brand but validator misses it, report as a bug

---

### File Upload Fails

**Symptoms:**
- Cannot select file or upload doesn't work
- No image preview appears

**Solutions:**
1. Check file size (must be under 16MB) - all test images are well under this
2. Verify file format (PNG, JPG, JPEG only) - all test images should be PNG
3. **Live demo:** Wait 30-60 seconds if it's the first request (cold start)

---

### Live Demo is Slow or Times Out

**Symptoms:**
- Request takes very long
- Timeout errors

**Solutions:**
1. **First request:** Wait 30-60 seconds - Railway free tier has cold starts
2. Try refreshing the page and submitting again

---

## Configuration

Test behavior can be adjusted in `config.py` (local testing only):
```python
SIMILARITY_THRESHOLD = 0.85  # Brand name matching (0.0 to 1.0)
ABV_TOLERANCE = 0.3          # Alcohol content tolerance (±%)
```

**Effects:**
- Lower `SIMILARITY_THRESHOLD` = more lenient brand matching
- Higher `ABV_TOLERANCE` = accept larger differences in alcohol content

**Note:** Live demo uses the deployed configuration values.

---