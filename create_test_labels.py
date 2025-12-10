from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

def get_font_size_for_text(draw, text, max_width, initial_size, font_path):
    """Find the largest font size that fits the text within max_width"""
    try:
        font_size = initial_size
        while font_size > 10:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
                return font
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                return font
            
            font_size -= 2
        
        try:
            return ImageFont.truetype(font_path, 10)
        except:
            return ImageFont.load_default()
    except:
        return ImageFont.load_default()

def wrap_text(text, max_width, font, draw):
    """Wrap text to fit within max_width"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def create_label(filename, brand, product_type, abv, volume, include_warning=True):
    """Create a test alcohol label image with proper text fitting"""
    
    width, height = 600, 900
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    font_paths = {
        'bold': "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        'regular': "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    }
    
    max_text_width = width - 100
    
    try:
        font_brand_path = font_paths['bold']
        font_regular_path = font_paths['regular']
        
        font_brand = get_font_size_for_text(draw, brand.upper(), max_text_width, 50, font_brand_path)
        font_large = ImageFont.truetype(font_paths['bold'], 35)
        font_medium = ImageFont.truetype(font_paths['regular'], 28)
        font_small = ImageFont.truetype(font_paths['regular'], 18)
        font_tiny = ImageFont.truetype(font_paths['regular'], 14)
        print(f"  Loaded fonts for {filename}")
    except Exception as e:
        print(f"  Using default font for {filename}: {e}")
        font_brand = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_tiny = ImageFont.load_default()
    
    y = 60
    
    # Draw brand name
    brand_lines = wrap_text(brand.upper(), max_text_width, font_brand, draw)
    for line in brand_lines:
        draw.text((width/2, y), line, fill='black', font=font_brand, anchor="mt")
        bbox = draw.textbbox((width/2, y), line, font=font_brand, anchor="mt")
        line_height = bbox[3] - bbox[1]
        y += line_height + 10
    
    y += 20
    
    # Draw product type
    try:
        font_product = get_font_size_for_text(draw, product_type, max_text_width, 35, font_paths['bold'])
    except:
        font_product = font_large
    
    product_lines = wrap_text(product_type, max_text_width, font_product, draw)
    for line in product_lines:
        draw.text((width/2, y), line, fill='black', font=font_product, anchor="mt")
        bbox = draw.textbbox((width/2, y), line, font=font_product, anchor="mt")
        line_height = bbox[3] - bbox[1]
        y += line_height + 10
    
    y += 30
    
    # Draw alcohol content
    draw.text((width/2, y), f"{abv}% Alc./Vol.", fill='black', font=font_medium, anchor="mt")
    y += 60
    
    # Draw volume
    draw.text((width/2, y), volume, fill='black', font=font_medium, anchor="mt")
    y += 80
    
    # Draw decorative line
    draw.line([(50, y), (width-50, y)], fill='gray', width=2)
    y += 30
    
    # Draw manufacturer info
    draw.text((width/2, y), "Distilled and Bottled by", fill='gray', font=font_small, anchor="mt")
    y += 25
    
    brand_small_lines = wrap_text(brand, max_text_width, font_small, draw)
    for line in brand_small_lines:
        draw.text((width/2, y), line, fill='gray', font=font_small, anchor="mt")
        y += 22
    
    draw.text((width/2, y), "Louisville, Kentucky, USA", fill='gray', font=font_small, anchor="mt")
    y += 50
    
    # Draw government warning
    if include_warning:
        warning_y = height - 200
        draw.rectangle([(40, warning_y), (width-40, height-40)], outline='red', width=2)
        
        warning_y += 15
        draw.text((width/2, warning_y), "GOVERNMENT WARNING:", fill='red', font=font_small, anchor="mt")
        warning_y += 25
        
        warning_text = [
            "According to the Surgeon General, women should not",
            "drink alcoholic beverages during pregnancy because",
            "of the risk of birth defects. Consumption of alcoholic",
            "beverages impairs your ability to drive a car or",
            "operate machinery, and may cause health problems."
        ]
        
        for line in warning_text:
            draw.text((width/2, warning_y), line, fill='black', font=font_tiny, anchor="mt")
            warning_y += 18
    
    img.save(filename)
    print(f"  Created: {filename}")
    return filename

# Create test images directory
os.makedirs('test_images', exist_ok=True)

print("\nGenerating test label images...")
print("=" * 60)

# Test Case 1: Perfect Match - Bourbon
print("\n[1/10] Creating bourbon label (perfect match scenario)...")
create_label(
    'test_images/01_bourbon_perfect_match.png',
    brand='Old Tom Distillery',
    product_type='Kentucky Straight Bourbon Whiskey',
    abv='45',
    volume='750 mL',
    include_warning=True
)

# Test Case 2: Perfect Match - Vodka
print("[2/10] Creating vodka label (perfect match scenario)...")
create_label(
    'test_images/02_vodka_perfect_match.png',
    brand='Crystal Clear Vodka',
    product_type='Premium Vodka',
    abv='40',
    volume='1 L',
    include_warning=True
)

# Test Case 3: Missing Government Warning
print("[3/10] Creating gin label (missing warning scenario)...")
create_label(
    'test_images/03_gin_missing_warning.png',
    brand='Rebel Spirits',
    product_type='Craft Gin',
    abv='42',
    volume='750 mL',
    include_warning=False
)

# Test Case 4: Beer Label
print("[4/10] Creating beer label (perfect match scenario)...")
create_label(
    'test_images/04_beer_ipa.png',
    brand='Hoppy Hills Brewery',
    product_type='India Pale Ale',
    abv='6.5',
    volume='12 fl oz',
    include_warning=True
)

# Test Case 5: Wine Label
print("[5/10] Creating wine label (perfect match scenario)...")
create_label(
    'test_images/05_wine_cabernet.png',
    brand='Sunset Vineyards',
    product_type='Cabernet Sauvignon',
    abv='13.5',
    volume='750 mL',
    include_warning=True
)

# Test Case 6: High Proof Rum
print("[6/10] Creating rum label (perfect match scenario)...")
create_label(
    'test_images/06_rum_spiced.png',
    brand='Caribbean Gold',
    product_type='Spiced Rum',
    abv='47.5',
    volume='1 L',
    include_warning=True
)

# Test Case 7: Long Brand Name
print("[7/10] Creating label with long brand name...")
create_label(
    'test_images/07_long_brand_name.png',
    brand='Toms Old Distillery Premium Spirits Company',
    product_type='Small Batch Tennessee Whiskey',
    abv='43',
    volume='750 mL',
    include_warning=True
)

# Test Case 8: Complex Product Type
print("[8/10] Creating label with complex product type...")
create_label(
    'test_images/08_complex_product.png',
    brand='Heritage Distillers',
    product_type='Single Barrel Aged Kentucky Straight Bourbon Whiskey',
    abv='50',
    volume='750 mL',
    include_warning=True
)

# Test Case 9: Low ABV Beer
print("[9/10] Creating low ABV beer label...")
create_label(
    'test_images/09_beer_light.png',
    brand='Mountain Brew Co',
    product_type='Light Lager',
    abv='4.2',
    volume='12 fl oz',
    include_warning=True
)

# Test Case 10: High ABV Spirit
print("[10/10] Creating high ABV spirit label...")
create_label(
    'test_images/10_whiskey_cask_strength.png',
    brand='Barrel House Spirits',
    product_type='Cask Strength Rye Whiskey',
    abv='60',
    volume='750 mL',
    include_warning=True
)

print("All test images created successfully!")
print("Images saved in: test_images/")
