"""
Translation Service for Indian MSME document processing
Supports Google Translation API with fallback options
Handles Hindi, Tamil, Bengali, Marathi, and other Indian languages
"""

import os
import logging
from typing import Dict, Any, Optional, List
import asyncio
import re

# Google Translation API
try:
    from google.cloud import translate_v2 as translate
    TRANSLATE_AVAILABLE = True
except ImportError:
    TRANSLATE_AVAILABLE = False
    translate = None

# Fallback translation (basic word mapping for demo)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class TranslationService:
    """Translation service with Google Translation API and fallback options"""
    
    def __init__(self):
        self.translate_client = None
        self.gcp_project_id = os.environ.get('GCP_PROJECT_ID')
        self.translate_enabled = os.environ.get('TRANSLATE_ENABLED', 'false').lower() == 'true'
        self.target_languages = os.environ.get('TRANSLATE_TARGETS', 'hi,bn,ta,mr').split(',')
        self.confidence_threshold = float(os.environ.get('TRANSLATE_CONFIDENCE_THRESHOLD', '0.8'))
        
        # Basic fallback dictionaries for demo
        self.fallback_dicts = self._load_fallback_dicts()
        
        self._initialize_translate_client()
    
    def _initialize_translate_client(self):
        """Initialize Google Translation API client"""
        if not self.translate_enabled or not TRANSLATE_AVAILABLE:
            logger.info("Google Translation API not enabled or not available")
            return
        
        try:
            self.translate_client = translate.Client()
            logger.info("✓ Google Translation API client initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Translation client: {e}")
            self.translate_client = None
    
    def _load_fallback_dicts(self) -> Dict[str, Dict[str, str]]:
        """Load basic fallback translation dictionaries"""
        return {
            'hi': {
                'agreement': 'समझौता',
                'contract': 'अनुबंध',
                'payment': 'भुगतान',
                'terms': 'शर्तें',
                'conditions': 'शर्तें',
                'liability': 'दायित्व',
                'warranty': 'वारंटी',
                'termination': 'समाप्ति',
                'employment': 'रोजगार',
                'salary': 'वेतन',
                'wages': 'मजदूरी',
                'gst': 'जीएसटी',
                'tax': 'कर',
                'invoice': 'चालान',
                'bill': 'बिल'
            },
            'ta': {
                'agreement': 'ஒப்பந்தம்',
                'contract': 'ஒப்பந்தம்',
                'payment': 'பணம்',
                'terms': 'விதிமுறைகள்',
                'conditions': 'நிபந்தனைகள்',
                'liability': 'பொறுப்பு',
                'warranty': 'உத்தரவாதம்',
                'termination': 'முடிவு',
                'employment': 'வேலை',
                'salary': 'சம்பளம்',
                'wages': 'கூலி',
                'gst': 'ஜிஎஸ்டி',
                'tax': 'வரி',
                'invoice': 'விலைப்பட்டியல்',
                'bill': 'பில்'
            },
            'bn': {
                'agreement': 'চুক্তি',
                'contract': 'চুক্তি',
                'payment': 'পেমেন্ট',
                'terms': 'শর্তাবলী',
                'conditions': 'শর্তাবলী',
                'liability': 'দায়',
                'warranty': 'ওয়ারেন্টি',
                'termination': 'সমাপ্তি',
                'employment': 'চাকরি',
                'salary': 'বেতন',
                'wages': 'মজুরি',
                'gst': 'জিএসটি',
                'tax': 'কর',
                'invoice': 'চালান',
                'bill': 'বিল'
            },
            'mr': {
                'agreement': 'करार',
                'contract': 'करार',
                'payment': 'पेमेंट',
                'terms': 'अटी',
                'conditions': 'अटी',
                'liability': 'जबाबदारी',
                'warranty': 'वॉरंटी',
                'termination': 'समाप्ती',
                'employment': 'नोकरी',
                'salary': 'पगार',
                'wages': 'मजुरी',
                'gst': 'जीएसटी',
                'tax': 'कर',
                'invoice': 'चलन',
                'bill': 'बिल'
            }
        }
    
    async def translate_text(self, text: str, target_language: str, source_language: str = None) -> Dict[str, Any]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (hi, ta, bn, mr, en)
            source_language: Source language code (auto-detect if None)
            
        Returns:
            Dict with translated text, confidence, and metadata
        """
        if not text or not text.strip():
            return {
                'translated_text': text,
                'source_language': source_language or 'unknown',
                'target_language': target_language,
                'confidence': 0.0,
                'method': 'none',
                'error': 'Empty text provided'
            }
        
        # Try Google Translation API first
        if self.translate_client and self.translate_enabled:
            try:
                result = await self._translate_with_google(text, target_language, source_language)
                if result['confidence'] >= self.confidence_threshold:
                    return result
                else:
                    logger.warning(f"Google Translate confidence {result['confidence']} below threshold {self.confidence_threshold}")
            except Exception as e:
                logger.error(f"Google Translation failed: {e}")
        
        # Fallback to basic dictionary translation
        try:
            result = await self._translate_with_fallback(text, target_language, source_language)
            return result
        except Exception as e:
            logger.error(f"Fallback translation failed: {e}")
            return {
                'translated_text': text,  # Return original if all methods fail
                'source_language': source_language or 'unknown',
                'target_language': target_language,
                'confidence': 0.0,
                'method': 'none',
                'error': f"Translation failed: {str(e)}"
            }
    
    async def _translate_with_google(self, text: str, target_language: str, source_language: str = None) -> Dict[str, Any]:
        """Translate using Google Translation API"""
        try:
            # Prepare translation request
            if source_language:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.translate_client.translate(
                        text,
                        target_language=target_language,
                        source_language=source_language
                    )
                )
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.translate_client.translate(
                        text,
                        target_language=target_language
                    )
                )
            
            translated_text = result['translatedText']
            detected_source = result.get('detectedSourceLanguage', source_language or 'unknown')
            
            # Google doesn't provide confidence scores directly, so we estimate
            # based on text length and complexity
            confidence = self._estimate_confidence(text, translated_text)
            
            return {
                'translated_text': translated_text,
                'source_language': detected_source,
                'target_language': target_language,
                'confidence': confidence,
                'method': 'google',
                'metadata': {
                    'api_response': 'success',
                    'text_length': len(text),
                    'translated_length': len(translated_text)
                }
            }
            
        except Exception as e:
            logger.error(f"Google Translation API failed: {e}")
            raise
    
    async def _translate_with_fallback(self, text: str, target_language: str, source_language: str = None) -> Dict[str, Any]:
        """Translate using basic fallback dictionary"""
        if target_language not in self.fallback_dicts:
            return {
                'translated_text': text,
                'source_language': source_language or 'unknown',
                'target_language': target_language,
                'confidence': 0.0,
                'method': 'fallback',
                'error': f'Fallback dictionary not available for {target_language}'
            }
        
        dictionary = self.fallback_dicts[target_language]
        translated_words = []
        translated_count = 0
        
        # Simple word-by-word translation
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            if word in dictionary:
                translated_words.append(dictionary[word])
                translated_count += 1
            else:
                translated_words.append(word)  # Keep original if not found
        
        translated_text = ' '.join(translated_words)
        confidence = translated_count / len(words) if words else 0.0
        
        return {
            'translated_text': translated_text,
            'source_language': source_language or 'unknown',
            'target_language': target_language,
            'confidence': confidence,
            'method': 'fallback',
            'metadata': {
                'words_translated': translated_count,
                'total_words': len(words),
                'dictionary_size': len(dictionary)
            }
        }
    
    def _estimate_confidence(self, original: str, translated: str) -> float:
        """Estimate translation confidence based on heuristics"""
        if not original or not translated:
            return 0.0
        
        # Basic heuristics for confidence estimation
        confidence = 0.5  # Base confidence
        
        # Length ratio check
        length_ratio = len(translated) / len(original) if original else 0
        if 0.5 <= length_ratio <= 2.0:  # Reasonable length ratio
            confidence += 0.2
        
        # Character set check (if target is non-Latin)
        if any(ord(char) > 127 for char in translated):
            confidence += 0.1
        
        # Word count similarity
        orig_words = len(original.split())
        trans_words = len(translated.split())
        if orig_words > 0:
            word_ratio = trans_words / orig_words
            if 0.7 <= word_ratio <= 1.5:  # Reasonable word count ratio
                confidence += 0.2
        
        return min(confidence, 1.0)
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of the input text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with detected language and confidence
        """
        if not text or not text.strip():
            return {
                'language': 'unknown',
                'confidence': 0.0,
                'method': 'none'
            }
        
        # Try Google Translation API detection first
        if self.translate_client and self.translate_enabled:
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.translate_client.detect_language(text)
                )
                
                return {
                    'language': result['language'],
                    'confidence': result['confidence'],
                    'method': 'google'
                }
            except Exception as e:
                logger.error(f"Google language detection failed: {e}")
        
        # Fallback to basic detection
        return self._detect_language_fallback(text)
    
    def _detect_language_fallback(self, text: str) -> Dict[str, Any]:
        """Basic language detection using character sets"""
        if not text:
            return {'language': 'unknown', 'confidence': 0.0, 'method': 'fallback'}
        
        # Character set analysis
        total_chars = len(text)
        if total_chars == 0:
            return {'language': 'unknown', 'confidence': 0.0, 'method': 'fallback'}
        
        # Hindi (Devanagari)
        hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
        hindi_ratio = hindi_chars / total_chars
        
        # Tamil
        tamil_chars = sum(1 for char in text if '\u0B80' <= char <= '\u0BFF')
        tamil_ratio = tamil_chars / total_chars
        
        # Bengali
        bengali_chars = sum(1 for char in text if '\u0980' <= char <= '\u09FF')
        bengali_ratio = bengali_chars / total_chars
        
        # Marathi (similar to Hindi but with some unique characters)
        marathi_chars = sum(1 for char in text if char in 'ळक्षज्ञ')
        marathi_ratio = marathi_chars / total_chars
        
        # Determine language based on highest ratio
        ratios = {
            'hi': hindi_ratio,
            'ta': tamil_ratio,
            'bn': bengali_ratio,
            'mr': marathi_ratio,
            'en': 1.0 - max(hindi_ratio, tamil_ratio, bengali_ratio, marathi_ratio)
        }
        
        detected_lang = max(ratios, key=ratios.get)
        confidence = ratios[detected_lang]
        
        return {
            'language': detected_lang,
            'confidence': confidence,
            'method': 'fallback',
            'metadata': {
                'ratios': ratios,
                'total_chars': total_chars
            }
        }
    
    async def translate_document_analysis(self, analysis_result: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """
        Translate a complete document analysis result to target language
        
        Args:
            analysis_result: Complete analysis result from AI
            target_language: Target language code
            
        Returns:
            Translated analysis result
        """
        if target_language == 'en':
            return analysis_result  # No translation needed
        
        translated_result = analysis_result.copy()
        
        try:
            # Translate key text fields
            fields_to_translate = [
                'document_summary.main_purpose',
                'risk_assessment.red_flags',
                'risk_assessment.yellow_flags', 
                'risk_assessment.green_flags',
                'obligations.party_1_obligations',
                'obligations.party_2_obligations',
                'obligations.mutual_obligations'
            ]
            
            for field_path in fields_to_translate:
                try:
                    # Navigate to the field
                    parts = field_path.split('.')
                    current = translated_result
                    for part in parts[:-1]:
                        current = current.get(part, {})
                    
                    field_name = parts[-1]
                    if field_name in current:
                        if isinstance(current[field_name], list):
                            # Translate list items
                            translated_items = []
                            for item in current[field_name]:
                                if isinstance(item, str):
                                    trans_result = await self.translate_text(item, target_language)
                                    translated_items.append(trans_result['translated_text'])
                                else:
                                    translated_items.append(item)
                            current[field_name] = translated_items
                        elif isinstance(current[field_name], str):
                            # Translate string
                            trans_result = await self.translate_text(current[field_name], target_language)
                            current[field_name] = trans_result['translated_text']
                except Exception as e:
                    logger.warning(f"Failed to translate field {field_path}: {e}")
            
            # Add translation metadata
            translated_result['translation_metadata'] = {
                'target_language': target_language,
                'translated_at': asyncio.get_event_loop().time(),
                'translation_method': 'google' if self.translate_client else 'fallback'
            }
            
        except Exception as e:
            logger.error(f"Document analysis translation failed: {e}")
            translated_result['translation_error'] = str(e)
        
        return translated_result

# Global translation service instance
translation_service = TranslationService()
