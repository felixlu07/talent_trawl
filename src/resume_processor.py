"""
Resume Processor Module

Handles the core logic for processing resumes using Anthropic's Claude vision model.
Converts PDFs to images and extracts structured data based on configuration.
"""

import os
import logging
import base64
import json
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
import anthropic
from src.utils.pdf_helper import PDFHelper

logger = logging.getLogger(__name__)


class ResumeProcessor:
    """Processes resume PDFs and extracts structured data using LLM vision analysis"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize the resume processor
        
        Args:
            api_key: Anthropic API key
            model: Model identifier to use
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        logger.info(f"Initialized ResumeProcessor with model: {model}")
    
    def process_resume(
        self, 
        pdf_path: str, 
        job_role: str,
        questions: List[Dict[str, Any]],
        temp_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single resume PDF and extract structured data
        
        Args:
            pdf_path: Path to the PDF file
            job_role: Job role being evaluated for
            questions: List of question configurations with field names and types
            temp_dir: Optional temporary directory for image conversion
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        pdf_name = Path(pdf_path).stem
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {pdf_name}")
        logger.info(f"{'='*60}")
        
        # Validate PDF exists and has content
        if not os.path.exists(pdf_path):
            logger.error(f"❌ PDF not found: {pdf_path}")
            return self._create_error_result(pdf_name, "PDF file not found")
        
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            logger.error(f"❌ PDF is empty: {pdf_path}")
            return self._create_error_result(pdf_name, "PDF file is empty")
        
        logger.info(f"📄 PDF size: {file_size:,} bytes")
        
        # Create temp directory if not provided
        cleanup_temp = False
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp(prefix="talent_trawler_")
            cleanup_temp = True
            logger.info(f"📁 Created temp directory: {temp_dir}")
        
        try:
            # Convert PDF to images
            logger.info("🔄 Converting PDF to images...")
            image_paths = PDFHelper.convert_pdf_to_images(
                pdf_path, 
                temp_dir, 
                prefix=pdf_name
            )
            
            if not image_paths:
                logger.error("❌ Failed to convert PDF to images")
                return self._create_error_result(pdf_name, "PDF conversion failed")
            
            logger.info(f"✅ Converted {len(image_paths)} pages to images")
            
            # Validate images
            logger.info("🔍 Validating images...")
            valid_images = []
            for idx, img_path in enumerate(image_paths, 1):
                validation = PDFHelper.validate_image_file(img_path)
                if validation["is_valid"]:
                    logger.info(
                        f"  ✓ Page {idx}: {validation['width']}x{validation['height']}px, "
                        f"{validation['size']:,} bytes, {validation['format']}"
                    )
                    valid_images.append(img_path)
                else:
                    logger.warning(f"  ✗ Page {idx}: {validation['error']}")
            
            if not valid_images:
                logger.error("❌ No valid images after validation")
                return self._create_error_result(pdf_name, "No valid images generated")
            
            logger.info(f"✅ {len(valid_images)}/{len(image_paths)} images validated successfully")
            
            # Convert images to base64
            logger.info("🔄 Encoding images to base64...")
            encoded_images = []
            for img_path in valid_images:
                try:
                    encoded = PDFHelper.image_to_base64(img_path)
                    encoded_images.append(encoded)
                except Exception as e:
                    logger.warning(f"⚠️  Failed to encode {img_path}: {e}")
            
            if not encoded_images:
                logger.error("❌ Failed to encode any images")
                return self._create_error_result(pdf_name, "Image encoding failed")
            
            logger.info(f"✅ Encoded {len(encoded_images)} images")
            
            # Call LLM for analysis
            logger.info("🤖 Sending to LLM for analysis...")
            result = self._analyze_with_llm(
                encoded_images, 
                job_role, 
                questions,
                pdf_name
            )
            
            logger.info(f"✅ Analysis complete for {pdf_name}")
            logger.info(f"💰 Cost: ${result.get('cost_usd', 0):.4f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing {pdf_name}: {e}", exc_info=True)
            return self._create_error_result(pdf_name, str(e))
            
        finally:
            # Cleanup temp directory if we created it
            if cleanup_temp:
                try:
                    PDFHelper.cleanup_temp_files(temp_dir)
                    logger.info(f"🧹 Cleaned up temp directory")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to cleanup temp directory: {e}")
    
    def _analyze_with_llm(
        self, 
        encoded_images: List[str],
        job_role: str,
        questions: List[Dict[str, Any]],
        pdf_name: str
    ) -> Dict[str, Any]:
        """
        Send images to LLM for analysis and extract structured data
        
        Args:
            encoded_images: List of base64-encoded images
            job_role: Job role being evaluated for
            questions: List of question configurations
            pdf_name: Name of the PDF being processed
            
        Returns:
            Dictionary with extracted data
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(job_role, questions)
            
            # Build message content with images
            content = []
            
            # Add all images first
            for idx, encoded_img in enumerate(encoded_images, 1):
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": encoded_img
                    }
                })
            
            # Add the text prompt
            content.append({
                "type": "text",
                "text": prompt
            })
            
            # Make API call
            logger.info(f"📤 Sending {len(encoded_images)} images to {self.model}...")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": content
                }]
            )
            
            # Extract response text
            response_text = response.content[0].text
            logger.info(f"📥 Received response ({len(response_text)} chars)")
            
            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost_usd = self._calculate_cost(input_tokens, output_tokens)
            
            logger.info(f"📊 Tokens: {input_tokens:,} in / {output_tokens:,} out")
            logger.info(f"💰 Cost: ${cost_usd:.4f} USD")
            
            # Parse JSON response
            parsed_data = self._parse_llm_response(response_text, questions)
            
            # Add metadata
            result = {
                "filename": pdf_name,
                "status": "success",
                "pages_processed": len(encoded_images),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost_usd,
                **parsed_data
            }
            
            return result
            
        except anthropic.APIError as e:
            logger.error(f"❌ Anthropic API error: {e}")
            return self._create_error_result(pdf_name, f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"❌ LLM analysis error: {e}", exc_info=True)
            return self._create_error_result(pdf_name, f"Analysis error: {str(e)}")
    
    def _build_prompt(self, job_role: str, questions: List[Dict[str, Any]]) -> str:
        """
        Build the prompt for the LLM based on job role and questions
        
        Args:
            job_role: Job role being evaluated for
            questions: List of question configurations
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are analyzing a resume/CV for the position of: {job_role}

The images provided show all pages of the candidate's resume. Please analyze the resume carefully and extract the following information.

IMPORTANT: You must respond with ONLY a valid JSON object. Do not include any explanatory text before or after the JSON.

Extract the following fields:
"""
        
        for q in questions:
            field_name = q["field"]
            question = q["question"]
            data_type = q.get("type", "string")
            
            prompt += f"\n- {field_name} ({data_type}): {question}"
        
        prompt += """

Response format requirements:
1. Return ONLY a JSON object with the exact field names specified above
2. For numeric fields (int/float), use actual numbers, not strings
3. For string fields, provide concise answers using plain text only
4. If information is not available in the resume, use null for that field
5. Do not add any explanatory text outside the JSON object
6. CRITICAL: Use only plain ASCII text - no bullet points (•), no special unicode characters, no smart quotes
7. Use regular dashes (-), regular quotes ("), and numbered lists (1. 2. 3.) instead of bullets

Example response format:
{
  "field_name_1": value1,
  "field_name_2": value2,
  ...
}
"""
        
        return prompt
    
    def _parse_llm_response(
        self, 
        response_text: str, 
        questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Parse and validate the LLM response
        
        Args:
            response_text: Raw response from LLM
            questions: Question configurations for validation
            
        Returns:
            Parsed and validated data dictionary
        """
        try:
            # Try to find JSON in the response
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                # Remove first and last lines (``` markers)
                response_text = "\n".join(lines[1:-1])
                if response_text.startswith("json"):
                    response_text = "\n".join(response_text.split("\n")[1:])
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Validate and type-cast fields
            validated_data = {}
            for q in questions:
                field_name = q["field"]
                data_type = q.get("type", "string")
                value = data.get(field_name)
                
                # Type casting and validation
                if value is None or value == "":
                    validated_data[field_name] = None
                elif data_type == "int":
                    try:
                        validated_data[field_name] = int(float(value)) if value is not None else None
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️  Could not convert {field_name} to int: {value}")
                        validated_data[field_name] = None
                elif data_type == "float":
                    try:
                        validated_data[field_name] = float(value) if value is not None else None
                    except (ValueError, TypeError):
                        logger.warning(f"⚠️  Could not convert {field_name} to float: {value}")
                        validated_data[field_name] = None
                else:  # string or other
                    validated_data[field_name] = self._sanitize_string(str(value)) if value is not None else None
            
            return validated_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            # Return empty fields
            return {q["field"]: None for q in questions}
        except Exception as e:
            logger.error(f"❌ Error parsing response: {e}")
            return {q["field"]: None for q in questions}
    
    def _sanitize_string(self, text: str) -> str:
        """
        Sanitize string for CSV output by removing problematic characters
        
        Args:
            text: Input string to sanitize
            
        Returns:
            Cleaned string safe for CSV
        """
        if not text:
            return text
        
        # Replace common problematic characters
        replacements = {
            '•': '-',  # Bullet point to dash
            '●': '-',
            '◦': '-',
            '▪': '-',
            '▫': '-',
            '\u2022': '-',  # Unicode bullet
            '\u2023': '-',
            '\u25E6': '-',
            '\u2043': '-',
            '\u2219': '-',
            '"': '"',  # Smart quotes to regular quotes
            '"': '"',
            ''': "'",
            ''': "'",
            '–': '-',  # En dash to hyphen
            '—': '-',  # Em dash to hyphen
            '\n': ' ',  # Newlines to spaces
            '\r': ' ',
            '\t': ' ',  # Tabs to spaces
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove any remaining non-ASCII characters that might cause issues
        # Keep only printable ASCII and common punctuation
        text = ''.join(char if ord(char) < 128 or char in '°±²³µ' else ' ' for char in text)
        
        # Collapse multiple spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost in USD based on token usage
        
        Pricing (as of 2025):
        - Input: $3 per million tokens
        - Output: $15 per million tokens
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        return input_cost + output_cost
    
    def _create_error_result(self, pdf_name: str, error_message: str) -> Dict[str, Any]:
        """Create a standardized error result"""
        return {
            "filename": pdf_name,
            "status": "error",
            "error": error_message,
            "pages_processed": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0
        }
