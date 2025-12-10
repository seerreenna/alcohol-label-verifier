# Testing Guide for Alcohol Label Verification App

This guide provides testing instructions for the TTB Label Verification application.

## Table of Contents

1. [Setup](#setup)
2. [Generate Test Images](#generate-test-images)
3. [Test Scenarios](#test-scenarios)
4. [Expected Results](#expected-results)
5. [Troubleshooting](#troubleshooting)

---

## Setup

### Prerequisites

Ensure the application is running:
```bash
# Activate virtual environment
source venv/bin/activate

# Start the application
python run.py
```

Open browser to: `http://localhost:5000`

---

## Generate Test Images

Run the test image generator:
```bash
python create_test_labels.py
```

This creates 10 test images in `test_images/` directory, each designed to test specific scenarios.

**Generated Files:**
```
test_images/
├── 01_bourbon_perfect_match.png       # All fields correct
├── 02_vodka_perfect_match.png         # All fields correct
├── 03_gin_missing_warning.png         # Missing government warning
├── 04_beer_ipa.png                    # Beer label
├── 05_wine_cabernet.png               # Wine label
├── 06_rum_spiced.png                  # Rum label
├── 07_long_brand_name.png             # Tests text wrapping
├── 08_complex_product.png             # Complex product type
├── 09_beer_light.png                  # Low ABV beer
└── 10_whiskey_cask_strength.png       # High ABV spirit
```

---

## Test Scenarios

### Test 1: Perfect Match - Bourbon

**Purpose:** Verify all validations pass when data matches perfectly

**Form Inputs:**
```
Brand Name: Old Tom Distillery
Product Class/Type: Kentucky Straight Bourbon Whiskey
Alcohol Content: 45
Net Contents: 750 mL
```

**Image:** `test_images/01_bourbon_perfect_match.png`

**Expected Result:** ALL PASS

---

### Test 2: Perfect Match - Vodka

**Purpose:** Test with different beverage type

**Form Inputs:**
```
Brand Name: Crystal Clear Vodka
Product Class/Type: Premium Vodka
Alcohol Content: 40
Net Contents: 1 L
```

**Image:** `test_images/02_vodka_perfect_match.png`

**Expected Result:**  ALL PASS

---

### Test 3: Missing Government Warning

**Purpose:** Verify detection of missing mandatory warning

**Form Inputs:**
```
Brand Name: Rebel Spirits
Product Class/Type: Craft Gin
Alcohol Content: 42
Net Contents: 750 mL
```

**Image:** `test_images/03_gin_missing_warning.png`

**Expected Result:**  FAIL (Government Warning)
- Brand Name:  Pass
- Product Type:  Pass
- Alcohol Content:  Pass
- Net Contents:  Pass
- Government Warning:  FAIL - "Government warning statement not detected on label (required by TTB regulations)"

---

### Test 4: Brand Name Mismatch

**Purpose:** Test brand name validation

**Form Inputs:**
```
Brand Name: Wrong Brand Name  ← INTENTIONALLY WRONG
Product Class/Type: Kentucky Straight Bourbon Whiskey
Alcohol Content: 45
Net Contents: 750 mL
```

**Image:** `test_images/01_bourbon_perfect_match.png`

**Expected Result:**  FAIL (Brand Name)
- Brand Name:  FAIL - Mismatch detected
- Product Type:  Pass
- Alcohol Content:  Pass
- Net Contents:  Pass
- Government Warning:  Pass

---

### Test 5: Product Type Mismatch

**Purpose:** Test product type validation

**Form Inputs:**
```
Brand Name: Old Tom Distillery
Product Class/Type: Tequila  ← WRONG (label says Bourbon)
Alcohol Content: 45
Net Contents: 750 mL
```

**Image:** `test_images/01_bourbon_perfect_match.png`

**Expected Result:**  FAIL (Product Type)
- Brand Name:  Pass
- Product Type:  FAIL - "Product type 'Tequila' not found on label"
- Alcohol Content:  Pass
- Net Contents:  Pass
- Government Warning:  Pass

---

### Test 6: Alcohol Content Mismatch (Outside Tolerance)

**Purpose:** Test ABV validation with significant difference

**Form Inputs:**
```
Brand Name: Old Tom Distillery
Product Class/Type: Kentucky Straight Bourbon Whiskey
Alcohol Content: 40  ← WRONG (label says 45%, difference = 5%)
Net Contents: 750 mL
```

**Image:** `test_images/01_bourbon_perfect_match.png`

**Expected Result:**  FAIL (Alcohol Content)
- Brand Name:  Pass
- Product Type:  Pass
- Alcohol Content:  FAIL - "Alcohol content mismatch: Form says 40.0%, label shows 45.0%"
- Net Contents:  Pass
- Government Warning:  Pass

---

### Test 7: Alcohol Content Within Tolerance

**Purpose:** Test that small ABV differences are accepted

**Form Inputs:**
```
Brand Name: Old Tom Distillery
Product Class/Type: Kentucky Straight Bourbon Whiskey
Alcohol Content: 45.3  ← Slightly different (within ±0.3% tolerance)
Net Contents: 750 mL
```

**Image:** `test_images/01_bourbon_perfect_match.png`

**Expected Result:**  ALL PASS
- Alcohol Content:  "Alcohol content matches: 45.3% (form) ≈ 45.0% (label)"

**Note:** Tolerance is ±0.3%, so 44.7% to 45.3% would all pass

---

### Test 8: Net Contents Mismatch

**Purpose:** Test volume validation

**Form Inputs:**
```
Brand Name: Old Tom Distillery
Product Class/Type: Kentucky Straight Bourbon Whiskey
Alcohol Content: 45
Net Contents: 1 L  ← WRONG (label says 750 mL)
```

**Image:** `test_images/01_bourbon_perfect_match.png`

**Expected Result:**  FAIL (Net Contents)
- Brand Name:  Pass
- Product Type:  Pass
- Alcohol Content:  Pass
- Net Contents:  FAIL - "Net contents mismatch: Form says '1 L', label shows '750 mL'"
- Government Warning:  Pass

---

### Test 9: Case Insensitivity

**Purpose:** Verify case doesn't matter in matching

**Form Inputs:**
```
Brand Name: old tom distillery  ← all lowercase
Product Class/Type: KENTUCKY STRAIGHT BOURBON WHISKEY  ← all uppercase
Alcohol Content: 45
Net Contents: 750 ML  ← uppercase
```

**Image:** `test_images/01_bourbon_perfect_match.png`

**Expected Result:**  ALL PASS
- All fields should match despite case differences

---

### Test 10: Multiple Mismatches

**Purpose:** Verify all errors are reported, not just the first one

**Form Inputs:**
```
Brand Name: Wrong Brand
Product Class/Type: Wrong Type
Alcohol Content: 30
Net Contents: 2 L
```

**Image:** `test_images/01_bourbon_perfect_match.png`

**Expected Result:**  FAIL (Multiple Fields)
- Brand Name:  Mismatch
- Product Type:  Not found
- Alcohol Content:  Mismatch
- Net Contents:  Mismatch
- Government Warning:  Pass

**Important:** All errors should be shown, not just the first one

---

### Test 11: Beer Label (Low ABV)

**Purpose:** Test with low alcohol content beverage

**Form Inputs:**
```
Brand Name: Hoppy Hills Brewery
Product Class/Type: India Pale Ale
Alcohol Content: 6.5
Net Contents: 12 fl oz
```

**Image:** `test_images/04_beer_ipa.png`

**Expected Result:**  ALL PASS

---

### Test 12: Wine Label

**Purpose:** Test wine-specific validation

**Form Inputs:**
```
Brand Name: Sunset Vineyards
Product Class/Type: Cabernet Sauvignon
Alcohol Content: 13.5
Net Contents: 750 mL
```

**Image:** `test_images/05_wine_cabernet.png`

**Expected Result:**  ALL PASS

---

### Test 13: High ABV Spirit

**Purpose:** Test with high alcohol content

**Form Inputs:**
```
Brand Name: Barrel House Spirits
Product Class/Type: Cask Strength Rye Whiskey
Alcohol Content: 60
Net Contents: 750 mL
```

**Image:** `test_images/10_whiskey_cask_strength.png`

**Expected Result:**  ALL PASS

---

### Test 14: Invalid File Type

**Purpose:** Test error handling for non-image files

**Steps:**
1. Create a text file: `echo "test" > test.txt`
2. Fill form with any valid data
3. Try to upload `test.txt`

**Expected Result:**  ERROR
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

## Test Results Tracking

Use this checklist to track your testing progress:
```
□ Test 1: Bourbon Perfect Match
□ Test 2: Vodka Perfect Match
□ Test 3: Missing Government Warning
□ Test 4: Brand Name Mismatch
□ Test 5: Product Type Mismatch
□ Test 6: ABV Mismatch (Outside Tolerance)
□ Test 7: ABV Within Tolerance
□ Test 8: Net Contents Mismatch
□ Test 9: Case Insensitivity
□ Test 10: Multiple Mismatches
□ Test 11: Beer Label
□ Test 12: Wine Label
□ Test 13: High ABV Spirit
□ Test 14: Invalid File Type
```

---

## Troubleshooting

### OCR Returns No Text

**Symptoms:**
- Error: "Could not read text from label image"
- Error: "No text detected in image"

**Solutions:**
1. Check image quality - ensure it's clear and high resolution
2. Verify Tesseract is installed: `tesseract --version`
3. Check terminal logs for detailed error messages
4. Try regenerating test images: `python create_test_labels.py`

---

### All Validations Pass When They Shouldn't

**Symptoms:**
- Intentionally wrong data shows as matched

**Solutions:**
1. Check terminal logs to see what OCR extracted
2. Verify the form inputs exactly match the test case
3. Check for typos in form inputs
4. Review OCR extraction: Look for "OCR extracted text" in terminal

---

### Brand Name Not Detected

**Symptoms:**
- Brand name validation fails even with correct input
- Error: "Could not find brand name on label"

**Solutions:**
1. Check terminal logs for "Extracted brand name"
2. Try entering the brand name exactly as it appears on the label (check case)
3. If OCR text shows the brand, but validator misses it, there may be a typo

---

### File Upload Fails

**Symptoms:**
- Cannot select file or upload doesn't work
- No image preview appears

**Solutions:**
1. Check file size (must be under 16MB)
2. Verify file format (PNG, JPG, JPEG only)
3. Check browser console for JavaScript errors (F12)
4. Try a different browser

---


## Advanced Testing

### Test with Real Photos

For additional testing, you can:

1. Take photos of real alcohol labels with your phone
2. Transfer to your computer
3. Upload and test

**Note:** Real photos may have:
- Lower OCR accuracy (due to lighting, angle, reflections)
- Different formatting than generated images
- This tests the robustness of the OCR system

### Test Edge Cases

Try unusual scenarios:
- Very long brand names (20+ characters)
- Special characters in product names
- Unusual volume measurements (e.g., "750ml" vs "750 mL")
- Different units (fl oz vs mL vs L)
- Non-standard ABV formats

---



## Configuration

Test behavior can be adjusted in `config.py`:
```python
SIMILARITY_THRESHOLD = 0.85  # Brand name matching (0.0 to 1.0)
ABV_TOLERANCE = 0.3          # Alcohol content tolerance (±%)
```

Lower `SIMILARITY_THRESHOLD` = more lenient brand matching
Higher `ABV_TOLERANCE` = accept larger differences in alcohol content

---

## Additional Resources

- **TTB Guidelines**: https://www.ttb.gov/
- **Tesseract OCR Documentation**: https://github.com/tesseract-ocr/tesseract
- **Flask Testing Documentation**: https://flask.palletsprojects.com/en/latest/testing/

---

