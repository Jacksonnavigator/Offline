"""
Camera module for capturing images and live preview
"""

import cv2
import numpy as np
from typing import Optional, Tuple, Callable
from pathlib import Path
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class CameraCapture:
    """Handles camera initialization, preview, and image capture"""
    
    def __init__(self, device_id: int = 0, width: int = 1920, height: int = 1080, fps: int = 30):
        """
        Initialize camera capture
        
        Args:
            device_id: Camera device ID (0 for default)
            width: Frame width
            height: Frame height
            fps: Frames per second
        """
        self.device_id = device_id
        self.width = width
        self.height = height
        self.fps = fps
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.frame_count = 0
        
        logger.info(f"CameraCapture initialized: device={device_id}, resolution={width}x{height}, fps={fps}")
    
    def start_camera(self) -> bool:
        """
        Start camera capture
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.device_id)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera device {self.device_id}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer for live preview
            
            self.is_running = True
            self.frame_count = 0
            logger.info("Camera started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            return False
    
    def stop_camera(self) -> bool:
        """
        Stop camera capture
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.cap is not None:
                self.cap.release()
            self.is_running = False
            logger.info("Camera stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping camera: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from camera
        
        Returns:
            Frame as numpy array or None if capture fails
        """
        try:
            if self.cap is None or not self.cap.isOpened():
                logger.error("Camera not running")
                return None
            
            ret, frame = self.cap.read()
            
            if not ret:
                logger.warning("Failed to read frame from camera")
                return None
            
            self.frame_count += 1
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def capture_image(self, output_path: Optional[str] = None) -> Optional[str]:
        """
        Capture and save image from camera
        
        Args:
            output_path: Path to save image. If None, generates default path with timestamp
        
        Returns:
            Path to saved image or None if capture fails
        """
        try:
            frame = self.capture_frame()
            if frame is None:
                return None
            
            # Generate output path if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path("./documents")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / f"capture_{timestamp}.jpg")
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save image
            success = cv2.imwrite(output_path, frame)
            if success:
                logger.info(f"Image captured and saved to {output_path}")
                return output_path
            else:
                logger.error(f"Failed to save image to {output_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            return None
    
    def get_frame_info(self) -> Tuple[int, int, int]:
        """
        Get current frame information
        
        Returns:
            Tuple of (width, height, frame_count)
        """
        try:
            if self.cap is None:
                return 0, 0, 0
            
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height, self.frame_count
            
        except Exception as e:
            logger.error(f"Error getting frame info: {e}")
            return 0, 0, 0
    
    def list_available_cameras(self) -> list:
        """
        List available camera devices
        
        Returns:
            List of available camera device IDs
        """
        available = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        
        logger.info(f"Available cameras: {available}")
        return available
    
    def __enter__(self):
        """Context manager entry"""
        self.start_camera()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_camera()
