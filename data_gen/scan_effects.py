"""
Scan Effects Module

Shared module for adding realistic scanning artifacts to PDF documents.
Used by both local scripts and Databricks notebooks to ensure identical functionality.

Functions:
- add_noise(): Add random noise to images
- add_blur(): Add blur to simulate poor resolution
- adjust_brightness(): Adjust brightness for faded scans
- add_rotation(): Add slight rotation for skewed scans
- apply_scan_effects(): Apply combination of effects
- process_pdf(): Convert PDF, apply effects, save as new PDF
"""

import random
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from pdf2image import convert_from_path


# ==============================================================================
# SCAN EFFECT PARAMETERS (Shared Configuration)
# ==============================================================================

SCAN_EFFECT_DISTRIBUTION = {
    "pristine": 0.70,      # 70% clean PDFs
    "light_scan": 0.20,    # 20% lightly scanned
    "heavy_scan": 0.10,    # 10% heavily scanned/degraded
}

SCAN_EFFECTS = {
    "pristine": {
        "noise": 0,
        "blur": 0,
        "rotation": 0,
        "brightness": 1.0,
    },
    "light": {
        "noise": 5,
        "blur": 0.5,
        "rotation": 0.5,
        "brightness": 0.95,
    },
    "heavy": {
        "noise": 15,
        "blur": 1.5,
        "rotation": 1.5,
        "brightness": 0.85,
    },
}


# ==============================================================================
# IMAGE EFFECT FUNCTIONS
# ==============================================================================

def add_noise(image, intensity=10):
    """
    Add random noise to simulate scanning artifacts.
    
    Args:
        image: PIL Image object
        intensity: Noise intensity (0-255), higher = more noise
    
    Returns:
        PIL Image with noise added
    """
    img_array = np.array(image)
    noise = np.random.randint(-intensity, intensity, img_array.shape, dtype='int16')
    noisy_img = np.clip(img_array + noise, 0, 255).astype('uint8')
    return Image.fromarray(noisy_img)


def add_blur(image, radius=1):
    """
    Add blur to simulate poor scanning resolution.
    
    Args:
        image: PIL Image object
        radius: Blur radius in pixels
    
    Returns:
        Blurred PIL Image
    """
    return image.filter(ImageFilter.GaussianBlur(radius=radius))


def adjust_brightness(image, factor=0.9):
    """
    Adjust brightness to simulate faded scans or photocopies.
    
    Args:
        image: PIL Image object
        factor: Brightness factor (< 1 = darker, > 1 = brighter)
    
    Returns:
        PIL Image with adjusted brightness
    """
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)


def add_rotation(image, angle=0.5):
    """
    Add slight rotation to simulate skewed scanning.
    
    Args:
        image: PIL Image object
        angle: Rotation angle in degrees (positive = counterclockwise)
    
    Returns:
        Rotated PIL Image with white fill
    """
    return image.rotate(angle, fillcolor='white', expand=False)


def apply_scan_effects(image, quality='light'):
    """
    Apply a combination of effects to simulate scanned documents.
    
    This is the main function that applies multiple effects based on quality level.
    
    Args:
        image: PIL Image object
        quality: 'pristine', 'light' or 'heavy' - determines effect intensity
    
    Returns:
        PIL Image with scan effects applied
    """
    if quality == 'pristine':
        # No effects - return as-is
        return image
        
    elif quality == 'light':
        # Light scanning effects - minimal degradation
        image = add_noise(image, intensity=5)
        image = add_blur(image, radius=0.5)
        image = adjust_brightness(image, factor=0.95)
        image = add_rotation(image, angle=random.uniform(-0.5, 0.5))
        
    elif quality == 'heavy':
        # Heavy scanning effects - significant degradation
        image = add_noise(image, intensity=15)
        image = add_blur(image, radius=1.5)
        image = adjust_brightness(image, factor=0.85)
        image = add_rotation(image, angle=random.uniform(-1.5, 1.5))
        # Ensure RGB mode for compression artifacts
        if image.mode != 'RGB':
            image = image.convert('RGB')
    
    return image


# ==============================================================================
# PDF PROCESSING FUNCTION
# ==============================================================================

def process_pdf(input_path, output_path, quality='light', dpi=150):
    """
    Convert PDF to images, apply scan effects, and save as new PDF.
    
    This is the main function for processing entire PDF documents.
    
    Args:
        input_path: Path to input PDF (local filesystem path)
        output_path: Path to save processed PDF (local filesystem path)
        quality: Effect quality - 'pristine', 'light', or 'heavy'
        dpi: DPI for image conversion (lower = more degraded, typical: 72-300)
    
    Returns:
        bool: True if successful, False otherwise
    
    Raises:
        Exception: If PDF processing fails
    """
    try:
        # Convert PDF to images at specified DPI
        images = convert_from_path(input_path, dpi=dpi)
        
        # Apply effects to each page
        processed_images = []
        for image in images:
            processed = apply_scan_effects(image, quality=quality)
            processed_images.append(processed)
        
        # Save as new PDF
        if processed_images:
            # Ensure all images are in RGB mode
            rgb_images = []
            for img in processed_images:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                rgb_images.append(img)
            
            # Determine JPEG quality based on scan quality
            jpeg_quality = {
                'pristine': 95,
                'light': 85,
                'heavy': 70
            }.get(quality, 85)
            
            # Save multi-page PDF
            rgb_images[0].save(
                output_path,
                save_all=True,
                append_images=rgb_images[1:] if len(rgb_images) > 1 else [],
                resolution=dpi,
                quality=jpeg_quality
            )
        
        return True
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def determine_quality(distribution=None):
    """
    Randomly determine document quality based on distribution.
    
    Args:
        distribution: Optional dict with quality distribution weights
                     Default uses SCAN_EFFECT_DISTRIBUTION
    
    Returns:
        str: Quality level ('pristine', 'light', or 'heavy')
    """
    if distribution is None:
        distribution = SCAN_EFFECT_DISTRIBUTION
    
    rand = random.random()
    cumulative = 0
    
    for quality, weight in distribution.items():
        cumulative += weight
        if rand < cumulative:
            return quality.replace('_scan', '')  # Return 'light' not 'light_scan'
    
    return 'light'  # Default fallback


def get_quality_params(quality):
    """
    Get effect parameters for a given quality level.
    
    Args:
        quality: Quality level string
    
    Returns:
        dict: Effect parameters (noise, blur, rotation, brightness)
    """
    return SCAN_EFFECTS.get(quality, SCAN_EFFECTS['light'])


# ==============================================================================
# BATCH PROCESSING HELPER
# ==============================================================================

def process_pdf_batch(pdf_paths, output_dir, quality_distribution=None, 
                     dpi=150, percentage=30):
    """
    Process a batch of PDFs with scan effects.
    
    Args:
        pdf_paths: List of (input_path, filename) tuples
        output_dir: Directory to save processed PDFs
        quality_distribution: Optional quality distribution dict
        dpi: DPI for conversion
        percentage: Percentage of PDFs to process (0-100)
    
    Returns:
        tuple: (processed_count, failed_count, results_list)
    """
    import os
    
    # Select random subset based on percentage
    num_to_process = int(len(pdf_paths) * percentage / 100)
    selected = random.sample(pdf_paths, min(num_to_process, len(pdf_paths)))
    
    processed_count = 0
    failed_count = 0
    results = []
    
    for input_path, filename in selected:
        # Determine quality
        quality = determine_quality(quality_distribution)
        
        # Create output filename
        output_filename = f"scanned_{quality}_{filename}"
        output_path = os.path.join(output_dir, output_filename)
        
        # Process PDF
        success = process_pdf(input_path, output_path, quality=quality, dpi=dpi)
        
        result = {
            'input': filename,
            'output': output_filename,
            'quality': quality,
            'success': success
        }
        results.append(result)
        
        if success:
            processed_count += 1
        else:
            failed_count += 1
    
    return processed_count, failed_count, results
