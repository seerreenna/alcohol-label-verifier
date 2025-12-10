from difflib import SequenceMatcher
import re
from config import Config

class LabelValidator:
    """Service for validating form data against the data extracted from OCR"""
    
    def __init__(self):
        self.similarity_threshold = Config.SIMILARITY_THRESHOLD # stored in config file for easy changing
        self.abv_tolerance = Config.ABV_TOLERANCE

    def calculate_similarity(self, str1, str2):
        """
        Calculate similarity between two strings (0.0 to 1.0)
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Float between 0 and 1 (1 = identical)
        """
        if not str1 or not str2: # if either is empty 
            return 0.0
        
        # Normalize both strings (lowercase + strip whitespace)
        s1 = str1.lower().strip()
        s2 = str2.lower().strip()

        # Using Gestalt Pattern Matching (longest matching seq between two strings)
        # returns ratio based on how much it matches
        return SequenceMatcher(None, s1, s2).ratio() 
        
    def validate_brand_name(self, form_brand, ocr_data):
        """
        Validate brand name from form against data extracted from OCR 
        
        Args:
            form_brand: Brand name from form
            ocr_data: OCR extracted data dictionary
            
        Returns:
            Dict with 'matched' (bool) and 'message' (str)
        """
        ocr_brand = ocr_data.get('brand_name')

        if not ocr_brand:
        # Find brand name in raw text
            raw_text = ocr_data.get('raw_text', '')

            if form_brand.lower() in raw_text.lower():
                return {
                    'matched': True,
                    'message': f"Brand name '{form_brand}' found in label text"
                }
            else:
                return {
                    'matched': False,
                    'message': f"Could not find brand name '{form_brand}' on label. OCR may have failed to read it clearly."
                }
        
        # Calculate similarity
        similarity = self.calculate_similarity(form_brand, ocr_brand)

        if similarity >= self.similarity_threshold:
            return {
                'matched': True,
                'message': f"Brand name matches: '{form_brand}' ≈ '{ocr_brand}' ({similarity*100:.0f}% similar)"
            }
        else:
            return {
                'matched': False,
                'message': f"Brand name mismatch: Form says '{form_brand}', label shows '{ocr_brand}'"
            }
        
    def validate_product_type(self, form_type, ocr_data):
        """
        Validate product type from form against data extracted from OCR 
        
        Args:
            form_type: Product type from form
            ocr_data: OCR extracted data dictionary
            
        Returns:
            Dict with 'matched' (bool) and 'message' (str)
        """
        raw_text = ocr_data.get('raw_text', '').lower()
        form_type_lower = form_type.lower()
        # Check for singular words
        form_words = form_type_lower.split()
        significant_words = [w for w in form_words if len(w) > 3]  # Ignore short words like "the", "and"
        matches = [word for word in significant_words if word in raw_text]

        # Check if product type appears in the text
        if form_type_lower in raw_text:
            return {
                'matched': True,
                'message': f"Product type '{form_type}' found on label"
            }

        if len(matches) >= len(significant_words) * 0.6:  # At least 60% of words found (does not need to be exact match)
            return {
                'matched': True,
                'message': f"Product type '{form_type}' partially matches label text (found: {', '.join(matches)})"
            }
        else:
            return {
                'matched': False,
                'message': f"Product type '{form_type}' not found on label. Label may use different wording."
            }
        
    def validate_alcohol_content(self, form_abv, ocr_data):
        """
        Validate alcohol content from form against data extracted from OCR 
        
        Args:
            form_abv: ABV from form (string or float)
            ocr_data: OCR extracted data dictionary
            
        Returns:
            Dict with 'matched' (bool) and 'message' (str)
        """
        # try to convert number string to float
        try:
            form_abv_float = float(form_abv)
        except (ValueError, TypeError):
            return {
                'matched': False,
                'message': f"Invalid alcohol content in form: '{form_abv}'" # number not listed correctly or not number at all
            }
        
        ocr_abv = ocr_data.get('alcohol_content')
    
        if ocr_abv is None:
            return {
                'matched': False,
                'message': f"Could not find alcohol content on label. Expected {form_abv_float}%" # not in correct format
            }
        # Check if within set tolerance bounds (in config file)
        difference = abs(form_abv_float - ocr_abv)


        if difference <= self.abv_tolerance:
            return {
                'matched': True,
                'message': f"Alcohol content matches: {form_abv_float}% (form) ≈ {ocr_abv}% (label)"
            }
        else:
            return {
                'matched': False,
                'message': f"Alcohol content mismatch: Form says {form_abv_float}%, label shows {ocr_abv}%"
            }
    def validate_net_contents(self, form_contents, ocr_data):
        """
        Validate net contents from form against data extracted from OCR 
        
        Args:
            form_contents: Net contents from form 
            ocr_data: OCR extracted data dictionary
            
        Returns:
            Dict with 'matched' (bool) and 'message' (str)
        """
        ocr_contents = ocr_data.get('net_contents')
        
        if not ocr_contents:
            return {
                'matched': False,
                'message': f"Could not find net contents on label. Expected '{form_contents}'"
            }
        
        # Normalize and compare
        form_normalized = re.sub(r'\s+', '', form_contents.lower())
        ocr_normalized = re.sub(r'\s+', '', ocr_contents.lower())
        
        if form_normalized in ocr_normalized or ocr_normalized in form_normalized:
            return {
                'matched': True,
                'message': f"Net contents matches: '{form_contents}' ≈ '{ocr_contents}'"
            }
        else:
            return {
                'matched': False,
                'message': f"Net contents mismatch: Form says '{form_contents}', label shows '{ocr_contents}'"
            }
        
    def validate_government_warning(self, ocr_data):
        """
        Check if government warning is present on label
        
        Args:
            ocr_data: OCR extracted data dictionary
            
        Returns:
            Dict with 'matched' (bool) and 'message' (str)
        """
        has_warning = ocr_data.get('has_government_warning', False)
        if has_warning:
            return {
                'matched': True,
                'message': 'Government warning statement found on label'
            }
        else:
            return {
                'matched': False,
                'message': 'Government warning statement not detected on label (required by TTB regulations)'
            }
        
    def validate_all(self, form_data, ocr_data):
        """
        Validate all fields from form against data extracted from OCR 
        
        Args:
            form_data: Dictionary with form inputs
            ocr_data: Dictionary with OCR extracted data
            
        Returns:
            Dictionary with validation results
        """
        # Validate each field by calling each val method
        results = {
            'brand_name': self.validate_brand_name(form_data.get('brand_name'), ocr_data),
            'product_type': self.validate_product_type(form_data.get('product_type'), ocr_data),
            'alcohol_content': self.validate_alcohol_content(form_data.get('alcohol_content'), ocr_data),
            'net_contents': self.validate_net_contents(form_data.get('net_contents'), ocr_data),  
            'government_warning': self.validate_government_warning(ocr_data),
        }

        
        # Calculate overall match
        overall_match = all(result['matched'] for result in results.values())

        return {
            'overall_match': overall_match,
            'field_checks': results,
            'ocr_data': ocr_data  # for debugging
        }