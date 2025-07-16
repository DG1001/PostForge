from PIL import Image
import os
import uuid
from werkzeug.utils import secure_filename
from typing import Dict

class ImageProcessor:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        self.max_size = 10 * 1024 * 1024  # 10MB
    
    def process_image(self, file) -> Dict:
        """Process uploaded image and return metadata"""
        if not self._allowed_file(file.filename):
            raise ValueError("Nicht unterstützter Dateityp")
        
        # Check file size
        file_content = file.read()
        if len(file_content) > self.max_size:
            raise ValueError("Datei zu groß (max. 10MB)")
        
        # Reset file pointer
        file.seek(0)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(self.upload_folder, filename)
        
        try:
            # Save original
            file.save(filepath)
            
            # Generate thumbnail
            thumb_path = self._create_thumbnail(filepath)
            
            # Get image metadata
            with Image.open(filepath) as img:
                width, height = img.size
                format = img.format
            
            return {
                'filename': filename,
                'original_filename': file.filename,
                'filepath': filepath,
                'file_size': len(file_content),
                'mime_type': file.content_type,
                'width': width,
                'height': height,
                'format': format,
                'thumbnail_path': thumb_path
            }
        
        except Exception as e:
            # Clean up if processing failed
            if os.path.exists(filepath):
                os.remove(filepath)
            raise ValueError(f"Fehler beim Verarbeiten des Bildes: {str(e)}")
    
    def _allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def _create_thumbnail(self, filepath: str, size: tuple = (300, 300)) -> str:
        """Create thumbnail image"""
        try:
            with Image.open(filepath) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumb_filename = f"thumb_{os.path.basename(filepath)}"
                thumb_path = os.path.join(self.upload_folder, thumb_filename)
                img.save(thumb_path, optimize=True, quality=85)
                
                return thumb_path
        
        except Exception as e:
            # If thumbnail creation fails, return original path
            return filepath
    
    def delete_image(self, filepath: str) -> bool:
        """Delete image file and its thumbnail"""
        try:
            # Delete original file
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Delete thumbnail if exists
            thumb_filename = f"thumb_{os.path.basename(filepath)}"
            thumb_path = os.path.join(self.upload_folder, thumb_filename)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
            
            return True
        
        except Exception as e:
            return False
    
    def get_image_info(self, filepath: str) -> Dict:
        """Get information about an image file"""
        try:
            with Image.open(filepath) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size': os.path.getsize(filepath)
                }
        except Exception as e:
            return None