"""
PDF Helper Utilities

This module provides utility functions for PDF processing operations such as 
downloading, converting to images, and other basic operations.
"""

import os
import logging
import base64
from pdf2image import convert_from_path
from PIL import Image
from pathlib import Path
from typing import List, Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Auto-configure Poppler path for Windows
def _setup_poppler_path():
    """Automatically add Poppler to PATH if found in common locations"""
    if os.name == 'nt':  # Windows only
        common_paths = [
            r"C:\Program Files\poppler-25.07.0\Library\bin",
            r"C:\Program Files\poppler\Library\bin",
            r"C:\poppler\Library\bin",
            r"C:\Program Files (x86)\poppler\Library\bin",
        ]
        
        for poppler_path in common_paths:
            if os.path.exists(poppler_path):
                if poppler_path not in os.environ['PATH']:
                    os.environ['PATH'] = poppler_path + os.pathsep + os.environ['PATH']
                    logger.info(f"✅ Added Poppler to PATH: {poppler_path}")
                return True
        
        logger.warning("⚠️  Poppler not found in common locations. PDF conversion may fail.")
        logger.warning("   Install from: https://github.com/oschwartz10612/poppler-windows/releases/")
        return False
    return True

# Run setup on module import
_setup_poppler_path()

class PDFHelper:
    """Helper class for PDF processing operations"""
    
    @staticmethod
    def validate_image_file(image_path: str) -> dict:
        """Validate an image file to ensure it exists and can be properly loaded"""
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return {
                    "is_valid": False,
                    "error": "File does not exist",
                    "path": image_path
                }
                
            # Check file size
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                return {
                    "is_valid": False,
                    "error": "File is empty (0 bytes)",
                    "path": image_path,
                    "size": 0
                }
                
            # Try to open and read the image
            try:
                img = Image.open(image_path)
                width, height = img.size
                
                # Record image details
                return {
                    "is_valid": True,
                    "path": image_path,
                    "size": file_size,
                    "width": width,
                    "height": height,
                    "format": img.format
                }
            except Exception as img_error:
                return {
                    "is_valid": False,
                    "error": f"Failed to open image: {str(img_error)}",
                    "path": image_path,
                    "size": file_size
                }
                
        except Exception as e:
            return {
                "is_valid": False,
                "error": f"Validation error: {str(e)}",
                "path": image_path
            }
    
    @staticmethod
    def convert_pdf_to_images(pdf_path: str, output_dir: str, prefix: str = "page") -> List[str]:
        """Convert all pages of a PDF file to images"""
        try:
            # Verify the PDF file exists and has content
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file does not exist: {pdf_path}")
                return []
                
            file_size = os.path.getsize(pdf_path)
            if file_size == 0:
                logger.error(f"PDF file is empty (0 bytes): {pdf_path}")
                return []
                
            # Removed verbose logging
            pass
            
            # Convert all pages of the PDF to images
            images = convert_from_path(pdf_path)
            if not images:
                logger.error("Failed to convert PDF to images")
                return []
            
            # Save each page as a separate image
            image_paths = []
            for i, image in enumerate(images):
                image_path = os.path.join(output_dir, f"{prefix}_{i+1}.jpg")
                image.save(image_path, 'JPEG', quality=95)
                
                # Verify the image was saved successfully
                if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                    image_paths.append(image_path)
                    # Removed verbose logging
                    pass
                else:
                    logger.error(f"Failed to save image {i+1} to {image_path}")
                
            # Only log total number of pages for billing purposes
            logger.info(f"📄 Document has {len(image_paths)} pages for billing calculation")
            
            # Return the results
            return image_paths
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    @staticmethod
    def image_to_base64(image_path: str) -> str:
        """Convert an image file to base64 encoding"""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    @staticmethod
    def cleanup_temp_files(temp_dir: str) -> None:
        """Clean up temporary files"""
        try:
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
                logger.info(f"Temporary directory cleaned up: {temp_dir}")
        except FileNotFoundError:
            logger.warning(f"Temporary directory does not exist: {temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {e}")