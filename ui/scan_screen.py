"""Scan screen for capturing and processing documents"""
import customtkinter as ctk
from camera.capture import CameraCapture
from camera.document_detection import DocumentDetector
from utils.image_utils import ImageUtils
from ocr.ocr_engine import OCREngine
from storage.document_manager import DocumentManager
from utils.logger import get_logger
import cv2
import PIL.Image
import PIL.ImageTk
import numpy as np
from threading import Thread

logger = get_logger(__name__)


class ScanScreen(ctk.CTkFrame):
    """Screen for scanning and processing documents"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.camera = None
        self.detector = DocumentDetector()
        self.ocr = OCREngine(engine=config.get('ocr', {}).get('engine', 'paddle'))
        self.doc_manager = DocumentManager()
        self.current_image = None
        self.is_camera_running = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        try:
            # Title
            title = ctk.CTkLabel(self, text="Scan Document", font=ctk.CTkFont(size=24, weight="bold"))
            title.pack(pady=20)
            
            # Main content frame
            content = ctk.CTkFrame(self)
            content.pack(fill="both", expand=True, padx=20, pady=10)
            content.grid_columnconfigure(0, weight=1)
            content.grid_rowconfigure(0, weight=1)
            
            # Camera preview area
            self.preview_label = ctk.CTkLabel(content, text="Camera Preview", bg_color="gray20")
            self.preview_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            
            # Control buttons frame
            button_frame = ctk.CTkFrame(content)
            button_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=10)
            
            start_cam_btn = ctk.CTkButton(button_frame, text="Start Camera", command=self._start_camera)
            start_cam_btn.pack(side="left", padx=5)
            
            capture_btn = ctk.CTkButton(button_frame, text="Capture", command=self._capture_image, state="disabled")
            capture_btn.pack(side="left", padx=5)
            self.capture_btn = capture_btn
            
            stop_cam_btn = ctk.CTkButton(button_frame, text="Stop Camera", command=self._stop_camera, state="disabled")
            stop_cam_btn.pack(side="left", padx=5)
            self.stop_cam_btn = stop_cam_btn
            
            # Results area
            results_frame = ctk.CTkFrame(content)
            results_frame.grid(row=0, column=1, sticky="nsew", rowspan=2, padx=5, pady=5)
            results_frame.grid_rowconfigure(1, weight=1)
            
            results_label = ctk.CTkLabel(results_frame, text="OCR Results", font=ctk.CTkFont(size=12, weight="bold"))
            results_label.pack(pady=5)
            
            self.results_text = ctk.CTkTextbox(results_frame, height=300, width=300)
            self.results_text.pack(fill="both", expand=True, padx=5, pady=5)
            
            save_btn = ctk.CTkButton(results_frame, text="Save Document", command=self._save_document, state="disabled")
            save_btn.pack(padx=5, pady=5)
            self.save_btn = save_btn
            
        except Exception as e:
            logger.error(f"Error creating scan screen: {e}")
    
    def _start_camera(self):
        try:
            if not self.is_camera_running:
                self.camera = CameraCapture()
                self.camera.start_camera()
                self.is_camera_running = True
                self.capture_btn.configure(state="normal")
                self.stop_cam_btn.configure(state="normal")
                
                # Start preview thread
                Thread(target=self._update_preview, daemon=True).start()
        except Exception as e:
            logger.error(f"Error starting camera: {e}")
    
    def _update_preview(self):
        try:
            while self.is_camera_running:
                frame = self.camera.capture_frame()
                if frame is not None:
                    # Resize for display
                    display_frame = cv2.resize(frame, (400, 300))
                    
                    # Convert to RGB and PIL
                    display_frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                    pil_image = PIL.Image.fromarray(display_frame_rgb)
                    photo = PIL.ImageTk.PhotoImage(pil_image)
                    
                    self.preview_label.configure(image=photo)
                    self.preview_label.image = photo
                    self.current_image = frame
        except Exception as e:
            logger.error(f"Error updating preview: {e}")
    
    def _capture_image(self):
        try:
            if self.current_image is not None:
                # Detect document
                contour = self.detector.detect_document(self.current_image)
                if contour is not None:
                    # Flatten document
                    flattened = self.detector.flatten_document(self.current_image, contour)
                    if flattened is not None:
                        # Enhance image
                        enhanced = ImageUtils.enhance_contrast(flattened)
                        enhanced = ImageUtils.remove_noise(enhanced)
                        
                        # Run OCR
                        ocr_result = self.ocr.extract_text(enhanced)
                        
                        if ocr_result:
                            self.results_text.delete("1.0", "end")
                            self.results_text.insert("1.0", ocr_result.get('text', ''))
                            self.save_btn.configure(state="normal")
                            self.current_ocr_result = ocr_result
                            logger.info("Document captured and processed")
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
    
    def _stop_camera(self):
        try:
            self.is_camera_running = False
            if self.camera:
                self.camera.stop_camera()
            self.capture_btn.configure(state="disabled")
            self.stop_cam_btn.configure(state="disabled")
        except Exception as e:
            logger.error(f"Error stopping camera: {e}")
    
    def _save_document(self):
        try:
            if hasattr(self, 'current_ocr_result'):
                text = self.results_text.get("1.0", "end")
                ocr_result = self.current_ocr_result
                
                doc_id = self.doc_manager.create_document(
                    title="Scanned Document",
                    content=text,
                    language=ocr_result.get('language', 'en'),
                    ocr_confidence=ocr_result.get('confidence', 0.0)
                )
                
                if doc_id:
                    logger.info(f"Document saved with ID: {doc_id}")
                    self.results_text.delete("1.0", "end")
                    self.results_text.insert("1.0", "Document saved successfully!")
        except Exception as e:
            logger.error(f"Error saving document: {e}")
