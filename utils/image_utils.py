"""
Image processing utilities for document scanning and OCR
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class ImageUtils:
    """Utility class for image processing operations"""
    
    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        """
        Load image from file path
        
        Args:
            image_path: Path to image file
        
        Returns:
            Image as numpy array or None if load fails
        """
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                logger.error(f"Failed to load image: {image_path}")
                return None
            return img
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: str) -> bool:
        """
        Save image to file
        
        Args:
            image: Image as numpy array
            output_path: Output file path
        
        Returns:
            True if successful, False otherwise
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            success = cv2.imwrite(str(output_path), image)
            if success:
                logger.info(f"Image saved to {output_path}")
            else:
                logger.error(f"Failed to save image to {output_path}")
            return success
        except Exception as e:
            logger.error(f"Error saving image to {output_path}: {e}")
            return False
    
    @staticmethod
    def resize_image(image: np.ndarray, width: int = 1920, height: int = 1080) -> np.ndarray:
        """
        Resize image to specified dimensions maintaining aspect ratio
        
        Args:
            image: Input image
            width: Target width
            height: Target height
        
        Returns:
            Resized image
        """
        try:
            h, w = image.shape[:2]
            aspect_ratio = w / h
            
            # Calculate new dimensions
            if w / width > h / height:
                new_w = width
                new_h = int(width / aspect_ratio)
            else:
                new_h = height
                new_w = int(height * aspect_ratio)
            
            return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return image
    
    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale
        
        Args:
            image: Input image (BGR)
        
        Returns:
            Grayscale image
        """
        try:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            logger.error(f"Error converting to grayscale: {e}")
            return image
    
    @staticmethod
    def apply_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """
        Apply Gaussian blur to image
        
        Args:
            image: Input image
            kernel_size: Blur kernel size
        
        Returns:
            Blurred image
        """
        try:
            if kernel_size % 2 == 0:
                kernel_size += 1
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        except Exception as e:
            logger.error(f"Error applying blur: {e}")
            return image
    
    @staticmethod
    def apply_edge_detection(image: np.ndarray, threshold1: int = 50, threshold2: int = 150) -> np.ndarray:
        """
        Apply Canny edge detection
        
        Args:
            image: Input image (grayscale)
            threshold1: Lower threshold
            threshold2: Upper threshold
        
        Returns:
            Edge detected image
        """
        try:
            return cv2.Canny(image, threshold1, threshold2)
        except Exception as e:
            logger.error(f"Error detecting edges: {e}")
            return image
    
    @staticmethod
    def apply_dilation(image: np.ndarray, kernel_size: int = 5, iterations: int = 2) -> np.ndarray:
        """
        Apply morphological dilation
        
        Args:
            image: Input image
            kernel_size: Kernel size
            iterations: Number of iterations
        
        Returns:
            Dilated image
        """
        try:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
            return cv2.dilate(image, kernel, iterations=iterations)
        except Exception as e:
            logger.error(f"Error applying dilation: {e}")
            return image
    
    @staticmethod
    def apply_thresholding(image: np.ndarray, threshold: int = 127) -> np.ndarray:
        """
        Apply binary thresholding
        
        Args:
            image: Input grayscale image
            threshold: Threshold value
        
        Returns:
            Binary image
        """
        try:
            _, binary = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
            return binary
        except Exception as e:
            logger.error(f"Error applying threshold: {e}")
            return image
    
    @staticmethod
    def apply_adaptive_thresholding(image: np.ndarray) -> np.ndarray:
        """
        Apply adaptive thresholding for better document detection
        
        Args:
            image: Input grayscale image
        
        Returns:
            Adaptively thresholded image
        """
        try:
            return cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
        except Exception as e:
            logger.error(f"Error applying adaptive threshold: {e}")
            return image
    
    @staticmethod
    def sharpen_image(image: np.ndarray) -> np.ndarray:
        """
        Sharpen image using unsharp masking
        
        Args:
            image: Input image
        
        Returns:
            Sharpened image
        """
        try:
            gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
            sharpened = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
            return np.clip(sharpened, 0, 255).astype(np.uint8)
        except Exception as e:
            logger.error(f"Error sharpening image: {e}")
            return image
    
    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast using CLAHE
        
        Args:
            image: Input image
        
        Returns:
            Contrast enhanced image
        """
        try:
            if len(image.shape) == 3:
                # For color images, convert to LAB, enhance L, convert back
                lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                l = clahe.apply(l)
                enhanced = cv2.merge([l, a, b])
                return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            else:
                # For grayscale
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                return clahe.apply(image)
        except Exception as e:
            logger.error(f"Error enhancing contrast: {e}")
            return image
    
    @staticmethod
    def remove_noise(image: np.ndarray) -> np.ndarray:
        """
        Remove noise using bilateral filter and morphological operations
        
        Args:
            image: Input image
        
        Returns:
            Denoised image
        """
        try:
            # Apply bilateral filter
            denoised = cv2.bilateralFilter(image, 9, 75, 75)
            return denoised
        except Exception as e:
            logger.error(f"Error removing noise: {e}")
            return image
    
    @staticmethod
    def deskew_image(image: np.ndarray) -> np.ndarray:
        """
        Deskew image (correct rotation)
        
        Args:
            image: Input image
        
        Returns:
            Deskewed image
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Get contours
            edges = cv2.Canny(gray, 100, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return image
            
            # Find largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get rotated bounding box
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[2]
            
            # Correct angle
            if angle < -45:
                angle = 90 + angle
            
            if abs(angle) > 1:  # Only rotate if angle is significant
                h, w = image.shape[:2]
                center = (w // 2, h // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(
                    image, rotation_matrix, (w, h),
                    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
                )
                return rotated
            
            return image
        except Exception as e:
            logger.error(f"Error deskewing image: {e}")
            return image
    
    @staticmethod
    def perspective_transform(image: np.ndarray, points: np.ndarray) -> np.ndarray:
        """
        Apply perspective transform to image
        
        Args:
            image: Input image
            points: 4 corner points for the transform
        
        Returns:
            Perspective transformed image
        """
        try:
            h, w = image.shape[:2]
            destination = np.array([
                [0, 0],
                [w, 0],
                [w, h],
                [0, h]
            ], dtype=np.float32)
            
            matrix = cv2.getPerspectiveTransform(points, destination)
            warped = cv2.warpPerspective(image, matrix, (w, h))
            return warped
        except Exception as e:
            logger.error(f"Error applying perspective transform: {e}")
            return image
    
    @staticmethod
    def get_image_dimensions(image: np.ndarray) -> Tuple[int, int]:
        """
        Get image dimensions (height, width)
        
        Args:
            image: Input image
        
        Returns:
            (height, width) tuple
        """
        return image.shape[:2]
    
    @staticmethod
    def convert_frame_to_rgb(frame: np.ndarray) -> np.ndarray:
        """
        Convert BGR frame to RGB for display
        
        Args:
            frame: BGR frame from OpenCV
        
        Returns:
            RGB frame
        """
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
