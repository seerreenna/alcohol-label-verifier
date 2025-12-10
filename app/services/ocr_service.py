import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import os 
from config import Config

class OCRService:
    """Service for extracting text from alcohol label images"""
    
    def __init__(self):
        """Initialize OCR service with Tesseract"""
        if Config.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD

    def preprocess_image(self, image_path):
        """
        Preprocess image to improve OCR accuracy
        
        Args:
            image_path: Path to the image file
            
        Returns:
            PIL Image object (preprocessed)
        """
        try:
            # Open image
            img = Image.open(image_path)
            # Convert to RGB, standardize formats such as png with transparency 
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # convert to grayscale (improves OCR)
            img = img.convert('L')

            # Increase contrast to improve 
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)

            # Sharpen image
            img = img.filter(ImageFilter.SHARPEN)

            # Resize image if too small (should be around 300px for Tesseract to work best with)
            width, height = img.size
            if width < 300:
                scale_factor = 300 / width
                new_size = (int(width * scale_factor), int(height * scale_factor))
                img = img.resize(new_size, Image.LANCZOS)
            
            return img
    
        except Exception as e:
            raise Exception(f"Error preprocessing image: {str(e)}")
        
    def extract_text(self, image_path):
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            dict with 'raw_text' and 'cleaned_text'
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return {
                    'raw_text': '',
                    'cleaned_text': '',
                    'success': False,
                    'error': f'Image file not found: {image_path}'
                }
            
            # Preprocess image using function above
            processed_img = self.preprocess_image(image_path)
            
            # Verify we have a valid image
            if processed_img is None:
                return {
                    'raw_text': '',
                    'cleaned_text': '',
                    'success': False,
                    'error': 'Failed to preprocess image'
                }
                
            # Extract text using Tesseract
            custom_config = r'--oem 3 --psm 6' # OEM 3: Using both Traditional and Neural Network based OCR. PSM 6: Assume text is a single block
            try:
                raw_text = pytesseract.image_to_string(processed_img, config=custom_config)
            except Exception as ocr_error:
                try:
                    raw_text = pytesseract.image_to_string(processed_img)
                except Exception as e:
                    return {
                        'raw_text': '',
                        'cleaned_text': '',
                        'success': False,
                        'error': f'Tesseract OCR failed: {str(e)}'
                    }

            # Alternative Config setting if above does not appear as single block of text
            try:
                custom_config_alt = r'--oem 3 --psm 11'# PSM 11: Good for scattered text when label is not written as block
                alt_text = pytesseract.image_to_string(processed_img, config=custom_config_alt)
                # Combine both for best results
                combined_text = raw_text + "\n" + alt_text
            except:
                combined_text = raw_text

            # Clean up text 
            cleaned_text = self._clean_text(combined_text)

            # Return raw and clean text 
            return {
                'raw_text': combined_text,
                'cleaned_text': cleaned_text,
                'success': True
            }
        
        # Add an exception to throw error if both raw and clean text fields are empty
        except Exception as e:
            return {
                'raw_text': '',
                'cleaned_text': '',
                'success': False,
                'error': str(e)
            }
        
    def _clean_text(self, text):
        """
        Clean and normalize OCR text
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text string
        """
        # Remove extra whitespace (leading, trailing, double)
        text = ' '.join(text.split())

        # Remove special characters that might throw an error in OCR (keep important punctuation such as %, ., -)
        text = re.sub(r'[^\w\s\.\-%]', '', text)

        return text

    def extract_brand_name(self, text):
        """
        Extract brand name from OCR text if available 
        Assume that it usually appears at the top in larger text
        
        Args:
            text: OCR extracted text
            
        Returns:
            Extracted brand name or None
        """
        # Split text into lines
        lines = text.split('\n')

        # words associated with product type or other label fields 
        product_type_words = [
            'warning', 'government', 'alcohol', 'vol', 'proof', 'alc',
            'whiskey', 'bourbon', 'vodka', 'wine', 'beer', 'gin', 'rum', 
            'tequila', 'scotch', 'rye', 'cognac', 'brandy',
            'distilled', 'bottled', 'ml', 'oz', 'liter', 'litre',
            'straight', 'kentucky', 'tennessee', 'single', 'double',
            'premium', 'craft', 'aged', 'reserve', 'special',
            'pale', 'ale', 'lager', 'stout', 'porter', 'ipa',
            'red', 'white', 'rose', 'sparkling', 'champagne',
            'cabernet', 'sauvignon', 'merlot', 'chardonnay', 'pinot',
            'small', 'batch', 'barrel', 'cask', 'oak',
            'spiced', 'flavored', 'infused', 'blended'
        ]

        candidates = []

        # Look for Brand name in in the first few lines
        for i, line in enumerate(lines[:10]):  # Check first 10 
            line = line.strip()
            words = line.split()
        
        # Skip empty lines
            if not line or len(line) <= 5:
                continue
            
            line_lower = line.lower()

            # Filter out common words that wouldn't be brand names
            if any(word in line_lower for word in product_type_words):
                continue

            # Skip if line contains percentages or volume measurements
            if '%' in line or any(unit in line_lower for unit in ['ml', 'oz', 'liter', 'litre', 'cl']):
                continue

            # Brand names are typically 2-5 words OR a single distinctive word
            if (2 <= len(words) <= 5) or (len(words) == 1 and len(line) > 8):
                candidates.append((i, line))
        if candidates:
            return candidates[0][1]
            
        return None
        
    def extract_alcohol_content(self, text):
        """
        Extract alcohol content (ABV) from text
        
        Args:
            text: OCR extracted text
            
        Returns:
            Float alcohol percentage or None
        """
        # Common pattern(s) for alcohol content
        patterns = [
            r'(\d+\.?\d*)\s*%\s*(?:alc|alcohol|abv)',  # "45% alc" or "45% ABV"
            r'(?:alc|alcohol|abv)\s*(\d+\.?\d*)\s*%',  # "alc 45%" or "ABV 45%"
            r'(\d+\.?\d*)\s*%\s*(?:vol|by\s*vol)',      # "45% vol" or "45% by vol"
            r'(\d+\.?\d*)\s*proof',                      # "90 proof" (divide by 2 for ABV)
        ]
        text_lower = text.lower() # lowercase text
        
        # search for patterns in text
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = float(match.group(1))

                # If it's proof, divide by 2 for ABV
                if 'proof' in pattern:
                    value = value / 2

                # Needs to be 0-100 (would not make sense o.w.)
                if 0 <= value <= 100:
                    return value
        
        return None

    def extract_net_contents(self, text):
        """
        Extract net contents AKA volume from text
        
        Args:
            text: OCR extracted text
            
        Returns:
            String with volume (e.g., "750 mL") or None
        """
        # Pattern(s) for volume
        patterns = [
            r'(\d+\.?\d*)\s*(ml|mL|ML|milliliters?)', 
            r'(\d+\.?\d*)\s*(l|L|liters?|litres?)', 
            r'(\d+\.?\d*)\s*(oz|OZ|fl\.?\s*oz|fluid\s*ounces?)',
            r'(\d+\.?\d*)\s*(cl|cL|CL|centiliters?)',
        ]

        # Search patterns
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1) # number
                unit = match.group(2) # unit
                return f"{value} {unit}"
            
        return None

    def check_government_warning(self, text):
        """
        Check if government warning text is present
        
        Args:
            text: OCR extracted text
            
        Returns:
            Boolean indicating if warning is present
        """
        text_lower = text.lower()
        
        # Key phrases that should appear in warning
        required_phrases = [
            'government warning',
            'surgeon general',
        ]

        # Check if at least the main phrase is present
        if 'government warning' in text_lower:
            return True
        
        # Check for "warning" and "surgeon general" separately
        if 'warning' in text_lower and 'surgeon general' in text_lower:
            return True
        
        return False

    def extract_all_info(self, image_path):
        """
        Extract all information from label image that is relevant
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with extracted information
        """
        # Extract text
        ocr_result = self.extract_text(image_path)
        
        if not ocr_result['success']:
            return {
                'success': False,
                'error': ocr_result.get('error', 'Failed to extract text from image')
            }
        
        text = ocr_result['raw_text']
        
        # Extract necessary fields
        extracted_data = {
            'success': True,
            'raw_text': text,
            'brand_name': self.extract_brand_name(text),
            'alcohol_content': self.extract_alcohol_content(text),
            'net_contents': self.extract_net_contents(text),
            'has_government_warning': self.check_government_warning(text),
        }
        
        return extracted_data