from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

from app.services.ocr_service import OCRService
from app.services.validator import LabelValidator

bp = Blueprint('main', __name__) # main blueprint

# Initialize services
ocr_service = OCRService()
validator = LabelValidator()

def allowed_file(filename):
    """Check if file extension is in allowable list"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']\

@bp.route('/')
def index():
    """ Main form page rendering"""
    return render_template('index.html')

@bp.route('/verify', methods=['POST'])
def verify_label():
    """Form submission handling and label verifying"""

    # Validate that file exists (to avoid someone submitting without file)
    if 'label_image' not in request.files:
        return render_template('results.html', 
                             error="No image file provided"), 400
    
    file = request.files['label_image']

    # Check if file name is empty
    if file.filename == '':
        return render_template('results.html', 
                             error="No image file selected"), 400
    
    # Validate file type with function above
    if not allowed_file(file.filename):
        return render_template('results.html', 
                             error="Invalid file type. Please upload PNG, JPG, or JPEG."), 400
    
    # Get form data and parse it into correct format
    form_data = {
        'brand_name': request.form.get('brand_name', '').strip(),
        'product_type': request.form.get('product_type', '').strip(),
        'alcohol_content': request.form.get('alcohol_content', '').strip(),
        'net_contents': request.form.get('net_contents', '').strip()
    }

    # Basic check to see if required fields are inputted in form
    if not form_data['brand_name'] or not form_data['product_type'] or not form_data['alcohol_content'] or not form_data['net_contents']:
        return render_template('results.html', 
                             error="Please fill in all required fields"), 400
    
    filepath = None
    # Save file temporarily
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        ocr_data = ocr_service.extract_all_info(filepath)
        
        current_app.logger.info(f"Processing image: {filename}")
        
        # Extract text from image using OCR
        ocr_data = ocr_service.extract_all_info(filepath)
        current_app.logger.info(f"OCR completed. Success: {ocr_data.get('success')}")
        
        if not ocr_data.get('success'):
            error_msg = ocr_data.get('error', 'Unknown error')
            current_app.logger.error(f"OCR failed: {error_msg}")
            return render_template('results.html', 
                                 error=f"Could not read text from label image. {error_msg}"), 500
        
        current_app.logger.info(f"OCR extracted text (first 200 chars): {ocr_data.get('raw_text', '')[:200]}")
        
        # Validate extracted data against form inputs
        validation_results = validator.validate_all(form_data, ocr_data)
        
        return render_template('results.html', 
                             results=validation_results, 
                             form_data=form_data)
     
    finally: # always deletes file no matter what
        # Clean up by removing uploaded file
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                current_app.logger.info(f"Cleaned up temporary file: {filename}")
            except Exception as e:
                current_app.logger.warning(f"Could not remove temporary file: {str(e)}")
    
@bp.route('/health')
def health_check():
    """Basic health check"""
    return jsonify({'status': 'healthy'}), 200



