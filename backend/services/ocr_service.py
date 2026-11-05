"""
OCR Service for Indian MSME document processing
Supports Google Vision API with Tesseract fallback
Handles handwritten, printed, and low-quality documents
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple
from io import BytesIO
import base64
import asyncio
from pathlib import Path

# Google Vision API
try:
    from google.cloud import vision
    from google.cloud.vision_v1 import types
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    vision = None

# Tesseract fallback
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None

logger = logging.getLogger(__name__)

class OCRService:
    """OCR service with Google Vision API and Tesseract fallback"""
    
    def __init__(self):
        self.vision_client = None
        self.gcp_project_id = os.environ.get('GCP_PROJECT_ID')
        self.gcp_region = os.environ.get('GCP_REGION', 'asia-south1')
        self.vision_enabled = os.environ.get('VISION_ENABLED', 'false').lower() == 'true'
        self.confidence_threshold = float(os.environ.get('OCR_CONFIDENCE_THRESHOLD', '0.7'))
        
        self._initialize_vision_client()
    
    def _initialize_vision_client(self):
        """Initialize Google Vision API client"""
        if not self.vision_enabled or not VISION_AVAILABLE:
            logger.info("Google Vision API not enabled or not available")
            return
        
        try:
            # Use service account key or default credentials
            self.vision_client = vision.ImageAnnotatorClient()
            logger.info("✓ Google Vision API client initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Vision client: {e}")
            self.vision_client = None
    
    async def extract_text_from_image(self, image_data: bytes, filename: str = None) -> Dict[str, Any]:
        """
        Extract text from image using Google Vision API with Tesseract fallback
        
        Args:
            image_data: Raw image bytes
            filename: Optional filename for context
            
        Returns:
            Dict with text, confidence, language, and metadata
        """
        result = {
            'text': '',
            'confidence': 0.0,
            'language': 'unknown',
            'method': 'none',
            'error': None,
            'metadata': {}
        }
        
        # Try Google Vision first if available
        if self.vision_client and self.vision_enabled:
            try:
                vision_result = await self._extract_with_vision(image_data)
                if vision_result['confidence'] >= self.confidence_threshold:
                    return vision_result
                else:
                    logger.warning(f"Vision confidence {vision_result['confidence']} below threshold {self.confidence_threshold}")
            except Exception as e:
                logger.error(f"Vision API failed: {e}")
                result['error'] = f"Vision API error: {str(e)}"
        
        # Fallback to Tesseract
        if TESSERACT_AVAILABLE:
            try:
                tesseract_result = await self._extract_with_tesseract(image_data)
                if tesseract_result['confidence'] > result['confidence']:
                    return tesseract_result
            except Exception as e:
                logger.error(f"Tesseract failed: {e}")
                if not result['error']:
                    result['error'] = f"Tesseract error: {str(e)}"
        
        # If all methods failed
        if not result['text']:
            result['error'] = "All OCR methods failed"
            logger.error("All OCR extraction methods failed")
        
        return result
    
    async def _extract_with_vision(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text using Google Vision API"""
        try:
            # Convert to Vision API format
            image = types.Image(content=image_data)
            
            # Perform text detection
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.vision_client.document_text_detection(image=image)
            )
            
            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")
            
            # Extract text and confidence
            texts = response.text_annotations
            if not texts:
                return {
                    'text': '',
                    'confidence': 0.0,
                    'language': 'unknown',
                    'method': 'vision',
                    'metadata': {'api_response': 'no_text_detected'}
                }
            
            # Get full text (first annotation is the complete text)
            full_text = texts[0].description
            confidence = 0.0
            
            # Calculate average confidence from individual words
            if len(texts) > 1:
                confidences = []
                for text in texts[1:]:  # Skip first (full text)
                    if hasattr(text, 'confidence') and text.confidence:
                        confidences.append(text.confidence)
                
                if confidences:
                    confidence = sum(confidences) / len(confidences)
            
            # Detect language (basic heuristic)
            language = self._detect_language(full_text)
            
            return {
                'text': full_text,
                'confidence': confidence,
                'language': language,
                'method': 'vision',
                'metadata': {
                    'text_count': len(texts),
                    'api_response': 'success'
                }
            }
            
        except Exception as e:
            logger.error(f"Vision API extraction failed: {e}")
            raise
    
    async def _extract_with_tesseract(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text using Tesseract OCR"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data))
            
            # Extract text with confidence data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Combine text and calculate confidence
            text_parts = []
            confidences = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:  # Skip empty/whitespace
                    text_parts.append(data['text'][i])
                    confidences.append(int(data['conf'][i]) / 100.0)  # Convert to 0-1 scale
            
            full_text = ' '.join(text_parts)
            confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Detect language
            language = self._detect_language(full_text)
            
            return {
                'text': full_text,
                'confidence': confidence,
                'language': language,
                'method': 'tesseract',
                'metadata': {
                    'word_count': len(text_parts),
                    'tesseract_version': pytesseract.get_tesseract_version()
                }
            }
            
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            raise
    
    def _detect_language(self, text: str) -> str:
        """Basic language detection for Indian languages"""
        if not text:
            return 'unknown'
        
        text_lower = text.lower()
        
        # Hindi indicators
        hindi_chars = set('अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')
        if any(char in text for char in hindi_chars):
            return 'hi'
        
        # Tamil indicators
        tamil_chars = set('அஆஇஈஉஊஎஏஐஒஓஔகஙசஜஞடணதநபமயரலவஶஷஸஹ')
        if any(char in text for char in tamil_chars):
            return 'ta'
        
        # Bengali indicators
        bengali_chars = set('অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহ')
        if any(char in text for char in bengali_chars):
            return 'bn'
        
        # Marathi indicators (similar to Hindi but with some unique characters)
        marathi_chars = set('ळक्षज्ञ')
        if any(char in text for char in marathi_chars):
            return 'mr'
        
        # Default to English if no Indian language detected
        return 'en'
    
    async def detect_document_type(self, text: str, filename: str = None) -> Dict[str, Any]:
        """
        Detect document type for specialized processing
        Returns type and confidence for routing to appropriate pipelines
        """
        if not text:
            return {'type': 'unknown', 'confidence': 0.0, 'indicators': []}
        
        text_lower = text.lower()
        indicators = []
        confidence = 0.0
        
        # GST Form indicators
        gst_indicators = [
            'gst', 'goods and services tax', 'gstr', 'cgst', 'sgst', 'igst',
            'tax invoice', 'bill of supply', 'credit note', 'debit note',
            'hsn code', 'sac code', 'gstin', 'tin number'
        ]
        gst_matches = sum(1 for indicator in gst_indicators if indicator in text_lower)
        if gst_matches > 0:
            indicators.extend([ind for ind in gst_indicators if ind in text_lower])
            confidence += gst_matches * 0.1
        
        # Labor law indicators
        labor_indicators = [
            'employment', 'employee', 'wages', 'salary', 'pf', 'esic', 'epf',
            'gratuity', 'bonus', 'overtime', 'working hours', 'leave',
            'contract of service', 'appointment letter', 'termination'
        ]
        labor_matches = sum(1 for indicator in labor_indicators if indicator in text_lower)
        if labor_matches > 0:
            indicators.extend([ind for ind in labor_indicators if ind in text_lower])
            confidence += labor_matches * 0.1
        
        # Commercial contract indicators
        contract_indicators = [
            'agreement', 'contract', 'terms and conditions', 'liability',
            'indemnity', 'force majeure', 'governing law', 'jurisdiction',
            'consideration', 'payment terms', 'delivery', 'warranty'
        ]
        contract_matches = sum(1 for indicator in contract_indicators if indicator in text_lower)
        if contract_matches > 0:
            indicators.extend([ind for ind in contract_indicators if ind in text_lower])
            confidence += contract_matches * 0.1
        
        # Invoice indicators
        invoice_indicators = [
            'invoice', 'bill', 'amount', 'total', 'subtotal', 'tax', 'vat',
            'due date', 'payment terms', 'net amount', 'gross amount'
        ]
        invoice_matches = sum(1 for indicator in invoice_indicators if indicator in text_lower)
        if invoice_matches > 0:
            indicators.extend([ind for ind in invoice_indicators if ind in text_lower])
            confidence += invoice_matches * 0.1
        
        # Determine primary type
        if gst_matches >= labor_matches and gst_matches >= contract_matches and gst_matches >= invoice_matches:
            doc_type = 'gst_form'
        elif labor_matches >= contract_matches and labor_matches >= invoice_matches:
            doc_type = 'labor_document'
        elif contract_matches >= invoice_matches:
            doc_type = 'commercial_contract'
        elif invoice_matches > 0:
            doc_type = 'invoice'
        else:
            doc_type = 'general_document'
        
        return {
            'type': doc_type,
            'confidence': min(confidence, 1.0),
            'indicators': list(set(indicators)),
            'filename_hint': filename
        }

# Global OCR service instance
ocr_service = OCRService()
