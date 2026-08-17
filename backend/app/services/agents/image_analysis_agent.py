"""
Image Analysis Agent - Analyzes uploaded images using Gemini Vision

This agent:
1. Analyzes screenshots, error messages, device photos
2. Extracts text using OCR (built into Gemini Vision)
3. Identifies the technical issue from the image
4. Returns structured data for the chat flow
"""
import logging
import base64
from typing import Dict, Optional, List
from pathlib import Path
import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ImageAnalysisAgent:
    """
    Gemini Vision-powered image analysis for IT support.
    Analyzes error screenshots, device photos, and technical issues.
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    MAX_IMAGE_SIZE = 4 * 1024 * 1024  # 4MB (Gemini limit)
    
    def __init__(self):
        """Initialize with Gemini Vision model."""
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        genai.configure(api_key=settings.google_api_key)
        
        # Use the vision-capable model
        # gemini-1.5-flash and gemini-2.0-flash support vision
        self.model = genai.GenerativeModel(
            settings.gemini_model,  # Should be gemini-1.5-flash or gemini-2.0-flash
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,  # Lower for analysis accuracy
                max_output_tokens=1000
            ),
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
            }
        )
        
        logger.info("Image Analysis Agent initialized")
    
    def analyze_image(
        self,
        image_data: bytes,
        mime_type: str,
        user_context: Optional[str] = None
    ) -> Dict:
        """
        Analyze an image and extract IT support information.
        
        Args:
            image_data: Raw image bytes
            mime_type: MIME type (image/jpeg, image/png, etc.)
            user_context: Optional user-provided context about the image
        
        Returns:
            {
                "success": bool,
                "extracted_text": str,  # Any text visible in image (error messages, etc.)
                "issue_description": str,  # Description of the visible issue
                "category": str,  # hardware, software, network, error, other
                "detected_elements": [],  # List of detected items (devices, screens, errors)
                "suggested_keywords": [],  # Keywords for RAG search
                "urgency_indicators": [],  # Any urgency signals detected
                "analysis_prompt": str  # Combined prompt for chat flow
            }
        """
        try:
            # Validate image
            if mime_type not in self.SUPPORTED_FORMATS:
                return self._error_response(f"Unsupported image format: {mime_type}")
            
            if len(image_data) > self.MAX_IMAGE_SIZE:
                return self._error_response(f"Image too large. Max size: {self.MAX_IMAGE_SIZE // (1024*1024)}MB")
            
            # Build analysis prompt
            analysis_prompt = self._build_analysis_prompt(user_context)
            
            # Create image part for Gemini
            image_part = {
                "mime_type": mime_type,
                "data": base64.standard_b64encode(image_data).decode("utf-8")
            }
            
            # Call Gemini Vision
            logger.info("[IMAGE-AGENT] Analyzing image...")
            response = self.model.generate_content([
                analysis_prompt,
                image_part
            ])
            
            if not response or not response.text:
                logger.warning("[IMAGE-AGENT] Empty response from Vision API")
                return self._error_response("Could not analyze the image")
            
            # Parse the structured response
            result = self._parse_analysis_response(response.text)
            result['success'] = True
            
            logger.info(f"[IMAGE-AGENT] Analysis complete: {result.get('issue_description', '')[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"[IMAGE-AGENT] Analysis error: {e}")
            return self._error_response(str(e))
    
    def _build_analysis_prompt(self, user_context: Optional[str] = None) -> str:
        """Build the analysis prompt for Gemini Vision."""
        prompt = """Analyze this image from an IT support context. Extract all relevant technical information.

## Your Task:
1. **Identify what's in the image** - Is it a screenshot, error message, device photo, etc.?
2. **Extract any visible text** - Error codes, messages, window titles, etc.
3. **Describe the technical issue** - What problem does this image show?
4. **Categorize the issue** - Hardware, software, network, or other?
5. **Note any urgency indicators** - Error severity, system warnings, etc.

## Response Format (provide as structured text):
EXTRACTED_TEXT: [Any text visible in the image, especially error messages]
ISSUE_DESCRIPTION: [Clear description of the technical problem shown]
CATEGORY: [hardware/software/network/error/other]
DETECTED_ELEMENTS: [List of items seen: device types, applications, error dialogs, etc.]
SUGGESTED_KEYWORDS: [Keywords that could help find similar issues: e.g., "BSOD", "outlook", "wifi"]
URGENCY_INDICATORS: [Any signs of urgency: critical errors, data loss warnings, etc.]

## Examples:

For a Blue Screen of Death (BSOD):
EXTRACTED_TEXT: DRIVER_IRQL_NOT_LESS_OR_EQUAL, Stop code: 0x000000D1
ISSUE_DESCRIPTION: Windows Blue Screen of Death (BSOD) showing DRIVER_IRQL_NOT_LESS_OR_EQUAL error, indicating a driver conflict or memory issue
CATEGORY: software
DETECTED_ELEMENTS: [BSOD screen, Windows error, QR code, error code]
SUGGESTED_KEYWORDS: [BSOD, blue screen, driver error, IRQL, crash]
URGENCY_INDICATORS: [System crash, potential data loss, repeated occurrence warning]

For a broken laptop screen:
EXTRACTED_TEXT: N/A
ISSUE_DESCRIPTION: Laptop screen showing visible cracks and display distortion, likely from physical damage
CATEGORY: hardware
DETECTED_ELEMENTS: [laptop, cracked screen, display damage]
SUGGESTED_KEYWORDS: [screen damage, cracked display, laptop screen]
URGENCY_INDICATORS: [Hardware damage requiring repair/replacement]

"""
        
        if user_context:
            prompt += f"\n## User's Description:\n\"{user_context}\"\n\nUse this context to better understand what the user is experiencing.\n"
        
        prompt += "\nAnalyze the image now:"
        
        return prompt
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse the structured response from Gemini Vision."""
        result = {
            "extracted_text": "",
            "issue_description": "",
            "category": "other",
            "detected_elements": [],
            "suggested_keywords": [],
            "urgency_indicators": [],
            "analysis_prompt": ""
        }
        
        lines = response_text.strip().split('\n')
        current_field = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('EXTRACTED_TEXT:'):
                result['extracted_text'] = line.replace('EXTRACTED_TEXT:', '').strip()
                current_field = 'extracted_text'
            elif line.startswith('ISSUE_DESCRIPTION:'):
                result['issue_description'] = line.replace('ISSUE_DESCRIPTION:', '').strip()
                current_field = 'issue_description'
            elif line.startswith('CATEGORY:'):
                category = line.replace('CATEGORY:', '').strip().lower()
                result['category'] = category if category in ['hardware', 'software', 'network', 'error', 'other'] else 'other'
                current_field = 'category'
            elif line.startswith('DETECTED_ELEMENTS:'):
                elements_str = line.replace('DETECTED_ELEMENTS:', '').strip()
                result['detected_elements'] = self._parse_list(elements_str)
                current_field = 'detected_elements'
            elif line.startswith('SUGGESTED_KEYWORDS:'):
                keywords_str = line.replace('SUGGESTED_KEYWORDS:', '').strip()
                result['suggested_keywords'] = self._parse_list(keywords_str)
                current_field = 'suggested_keywords'
            elif line.startswith('URGENCY_INDICATORS:'):
                urgency_str = line.replace('URGENCY_INDICATORS:', '').strip()
                result['urgency_indicators'] = self._parse_list(urgency_str)
                current_field = 'urgency_indicators'
            elif current_field and line:
                # Continue previous field if multi-line
                if current_field in ['extracted_text', 'issue_description']:
                    result[current_field] += ' ' + line
        
        # Build combined prompt for chat flow
        result['analysis_prompt'] = self._build_chat_prompt(result)
        
        return result
    
    def _parse_list(self, list_str: str) -> List[str]:
        """Parse a list string like '[item1, item2]' or 'item1, item2'."""
        # Remove brackets if present
        list_str = list_str.strip('[]')
        # Split by comma and clean up
        items = [item.strip().strip('"\'') for item in list_str.split(',')]
        return [item for item in items if item and item.lower() != 'n/a']
    
    def _build_chat_prompt(self, analysis: Dict) -> str:
        """Build a natural language prompt for the chat flow."""
        parts = []
        
        if analysis.get('issue_description'):
            parts.append(f"[Image Analysis] {analysis['issue_description']}")
        
        if analysis.get('extracted_text') and analysis['extracted_text'].lower() != 'n/a':
            parts.append(f"Visible text/error: {analysis['extracted_text']}")
        
        if analysis.get('detected_elements'):
            parts.append(f"Detected: {', '.join(analysis['detected_elements'])}")
        
        if analysis.get('urgency_indicators'):
            parts.append(f"Urgency: {', '.join(analysis['urgency_indicators'])}")
        
        return ' | '.join(parts) if parts else "Image uploaded for analysis"
    
    def _error_response(self, error_message: str) -> Dict:
        """Return an error response."""
        return {
            "success": False,
            "error": error_message,
            "extracted_text": "",
            "issue_description": f"Unable to analyze image: {error_message}",
            "category": "other",
            "detected_elements": [],
            "suggested_keywords": [],
            "urgency_indicators": [],
            "analysis_prompt": f"User uploaded an image (analysis failed: {error_message})"
        }
    
    def analyze_image_from_base64(
        self,
        base64_data: str,
        mime_type: str,
        user_context: Optional[str] = None
    ) -> Dict:
        """
        Analyze an image from base64-encoded data.
        
        Args:
            base64_data: Base64-encoded image data
            mime_type: MIME type of the image
            user_context: Optional user description
        
        Returns:
            Same as analyze_image()
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            image_bytes = base64.b64decode(base64_data)
            return self.analyze_image(image_bytes, mime_type, user_context)
            
        except Exception as e:
            logger.error(f"[IMAGE-AGENT] Base64 decode error: {e}")
            return self._error_response(f"Invalid base64 data: {e}")


# Global instance
_image_agent_instance = None

def get_image_analysis_agent() -> ImageAnalysisAgent:
    """Get or create the global image analysis agent instance."""
    global _image_agent_instance
    if _image_agent_instance is None:
        _image_agent_instance = ImageAnalysisAgent()
    return _image_agent_instance
