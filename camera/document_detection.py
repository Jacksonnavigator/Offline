"""
Document detection module for identifying and extracting documents from images
"""

import cv2
import numpy as np
from typing import Optional, List, Tuple
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentDetector:
    """Detects documents in images and performs perspective correction"""
    
    def __init__(self):
        """Initialize document detector"""
        self.min_contour_area = 5000  # Minimum contour area to be considered a document
        logger.info("DocumentDetector initialized")
    
    def detect_document(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect document in image and return document contour
        
        Args:
            image: Input image (BGR)
        
        Returns:
            Document contour as numpy array or None if no document found
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            
            # Dilate edges to connect broken lines
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            dilated = cv2.dilate(edges, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                logger.warning("No contours found in image")
                return None
            
            # Find largest quadrilateral contour
            doc_contour = self._find_document_contour(contours, image.shape)
            
            if doc_contour is None:
                logger.warning("No document contour found")
                return None
            
            logger.info("Document detected successfully")
            return doc_contour
            
        except Exception as e:
            logger.error(f"Error detecting document: {e}")
            return None
    
    def _find_document_contour(self, contours: List, image_shape: Tuple) -> Optional[np.ndarray]:
        """
        Find the largest quadrilateral contour that looks like a document
        
        Args:
            contours: List of contours
            image_shape: Shape of the image
        
        Returns:
            Document contour or None
        """
        h, w = image_shape[:2]
        
        # Filter and sort contours by area
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_contour_area:
                approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                
                # Check if contour is quadrilateral
                if len(approx) == 4:
                    valid_contours.append((area, approx))
        
        if not valid_contours:
            return None
        
        # Sort by area (largest first) and return the largest
        valid_contours.sort(key=lambda x: x[0], reverse=True)
        return valid_contours[0][1]
    
    def crop_document(self, image: np.ndarray, contour: np.ndarray) -> Optional[np.ndarray]:
        """
        Crop document region from image based on contour
        
        Args:
            image: Input image
            contour: Document contour (4 points)
        
        Returns:
            Cropped document image or None if crop fails
        """
        try:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            if w < 50 or h < 50:
                logger.warning(f"Document too small: {w}x{h}")
                return None
            
            # Crop image
            cropped = image[y:y+h, x:x+w].copy()
            logger.info(f"Document cropped: {w}x{h}")
            return cropped
            
        except Exception as e:
            logger.error(f"Error cropping document: {e}")
            return None
    
    def flatten_document(self, image: np.ndarray, contour: np.ndarray) -> Optional[np.ndarray]:
        """
        Apply perspective transform to flatten document (correct for camera angle)
        
        Args:
            image: Input image
            contour: Document contour (4 corner points)
        
        Returns:
            Flattened document image or None if transform fails
        """
        try:
            # Sort contour points
            points = contour.reshape(4, 2).astype(np.float32)
            points = self._order_points(points)
            
            # Get width and height of the output document
            width_top = np.linalg.norm(points[1] - points[0])
            width_bottom = np.linalg.norm(points[3] - points[2])
            max_width = int(max(width_top, width_bottom))
            
            height_left = np.linalg.norm(points[2] - points[0])
            height_right = np.linalg.norm(points[3] - points[1])
            max_height = int(max(height_left, height_right))
            
            # Define destination points
            dst_points = np.array([
                [0, 0],
                [max_width - 1, 0],
                [max_width - 1, max_height - 1],
                [0, max_height - 1]
            ], dtype=np.float32)
            
            # Get perspective transform matrix
            matrix = cv2.getPerspectiveTransform(points, dst_points)
            
            # Apply perspective transform
            warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
            logger.info(f"Document flattened: {max_width}x{max_height}")
            return warped
            
        except Exception as e:
            logger.error(f"Error flattening document: {e}")
            return None
    
    @staticmethod
    def _order_points(points: np.ndarray) -> np.ndarray:
        """
        Order points in correct order for perspective transform (top-left, top-right, bottom-right, bottom-left)
        
        Args:
            points: 4 corner points
        
        Returns:
            Ordered points
        """
        try:
            # Calculate center
            center = np.mean(points, axis=0)
            
            # Calculate angles from center
            angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
            
            # Sort by angle
            sorted_indices = np.argsort(angles)
            sorted_points = points[sorted_indices]
            
            # Ensure correct ordering: top-left, top-right, bottom-right, bottom-left
            # Find top-left (smallest x+y)
            sums = sorted_points[:, 0] + sorted_points[:, 1]
            top_left_idx = np.argmin(sums)
            
            # Rotate array so top-left is first
            ordered = np.roll(sorted_points, -top_left_idx, axis=0)
            
            return ordered
        except Exception as e:
            logger.error(f"Error ordering points: {e}")
            return points
    
    def get_document_area(self, contour: np.ndarray) -> float:
        """
        Calculate document area
        
        Args:
            contour: Document contour
        
        Returns:
            Contour area
        """
        return cv2.contourArea(contour)
    
    def draw_document_contour(self, image: np.ndarray, contour: np.ndarray, color: Tuple = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        """
        Draw document contour on image
        
        Args:
            image: Input image
            contour: Document contour
            color: BGR color for drawing
            thickness: Line thickness
        
        Returns:
            Image with drawn contour
        """
        try:
            result = image.copy()
            cv2.drawContours(result, [contour], 0, color, thickness)
            return result
        except Exception as e:
            logger.error(f"Error drawing contour: {e}")
            return image
    
    def is_document_visible(self, image: np.ndarray) -> bool:
        """
        Check if document is visible in frame
        
        Args:
            image: Input image
        
        Returns:
            True if document is detected
        """
        return self.detect_document(image) is not None
