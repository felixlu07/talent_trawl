"""
Configuration Handler Module

Handles loading, validating, and managing configuration files for resume processing.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ConfigHandler:
    """Handles configuration file loading and validation"""
    
    VALID_TYPES = ["string", "int", "float", "bool"]
    
    @staticmethod
    def load_config(config_path: str) -> Optional[Dict[str, Any]]:
        """
        Load and validate a configuration file
        
        Args:
            config_path: Path to the config.json file
            
        Returns:
            Validated configuration dictionary or None if invalid
        """
        try:
            logger.info(f"📋 Loading configuration from: {config_path}")
            
            if not Path(config_path).exists():
                logger.error(f"❌ Configuration file not found: {config_path}")
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate configuration
            if not ConfigHandler._validate_config(config):
                return None
            
            logger.info(f"✅ Configuration loaded successfully")
            logger.info(f"   Job Role: {config['job_role']}")
            logger.info(f"   Questions: {len(config['questions'])}")
            logger.info(f"   Output Format: {config.get('output_format', 'csv')}")
            
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in configuration file: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error loading configuration: {e}")
            return None
    
    @staticmethod
    def _validate_config(config: Dict[str, Any]) -> bool:
        """
        Validate configuration structure and content
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if "job_role" not in config:
            logger.error("❌ Configuration missing required field: job_role")
            return False
        
        if "questions" not in config:
            logger.error("❌ Configuration missing required field: questions")
            return False
        
        if not isinstance(config["questions"], list):
            logger.error("❌ 'questions' must be a list")
            return False
        
        if len(config["questions"]) == 0:
            logger.error("❌ 'questions' list cannot be empty")
            return False
        
        # Validate each question
        field_names = set()
        for idx, question in enumerate(config["questions"]):
            if not isinstance(question, dict):
                logger.error(f"❌ Question {idx} must be a dictionary")
                return False
            
            # Check required question fields
            if "field" not in question:
                logger.error(f"❌ Question {idx} missing required field: field")
                return False
            
            if "question" not in question:
                logger.error(f"❌ Question {idx} missing required field: question")
                return False
            
            # Check for duplicate field names
            field_name = question["field"]
            if field_name in field_names:
                logger.error(f"❌ Duplicate field name: {field_name}")
                return False
            field_names.add(field_name)
            
            # Validate data type if specified
            if "type" in question:
                data_type = question["type"]
                if data_type not in ConfigHandler.VALID_TYPES:
                    logger.error(
                        f"❌ Invalid type '{data_type}' for field '{field_name}'. "
                        f"Must be one of: {', '.join(ConfigHandler.VALID_TYPES)}"
                    )
                    return False
        
        # Validate output format if specified
        if "output_format" in config:
            output_format = config["output_format"].lower()
            if output_format not in ["csv", "json"]:
                logger.error(f"❌ Invalid output_format: {output_format}. Must be 'csv' or 'json'")
                return False
        
        return True
    
    @staticmethod
    def create_example_config(output_path: str, job_role: str = "Product Manager") -> None:
        """
        Create an example configuration file
        
        Args:
            output_path: Path where to save the example config
            job_role: Job role for the example (default: Product Manager)
        """
        example_config = {
            "job_role": job_role,
            "output_format": "csv",
            "questions": [
                {
                    "field": "candidate_name",
                    "question": "What is the candidate's full name?",
                    "type": "string"
                },
                {
                    "field": "email",
                    "question": "What is the candidate's email address?",
                    "type": "string"
                },
                {
                    "field": "phone",
                    "question": "What is the candidate's phone number?",
                    "type": "string"
                },
                {
                    "field": "total_years_experience",
                    "question": "How many total years of professional experience does the candidate have?",
                    "type": "float"
                },
                {
                    "field": "number_of_jobs",
                    "question": "How many different jobs/positions has the candidate held?",
                    "type": "int"
                },
                {
                    "field": "average_tenure_years",
                    "question": "What is the average tenure (in years) at each company the candidate has worked at?",
                    "type": "float"
                },
                {
                    "field": "highest_education",
                    "question": "What is the candidate's highest level of education (e.g., Bachelor's, Master's, PhD)?",
                    "type": "string"
                },
                {
                    "field": "has_product_management_experience",
                    "question": "Does the candidate have direct product management experience?",
                    "type": "bool"
                },
                {
                    "field": "years_product_management",
                    "question": "How many years of product management experience does the candidate have?",
                    "type": "float"
                },
                {
                    "field": "technical_skills",
                    "question": "List the key technical skills mentioned (comma-separated)",
                    "type": "string"
                },
                {
                    "field": "leadership_experience",
                    "question": "Does the resume demonstrate leadership experience? Provide a brief summary.",
                    "type": "string"
                },
                {
                    "field": "role_fit_score",
                    "question": "On a scale of 1-10, how well does this candidate fit the Product Manager role based on their experience and skills?",
                    "type": "int"
                },
                {
                    "field": "key_strengths",
                    "question": "What are the top 3 strengths of this candidate for a Product Manager role?",
                    "type": "string"
                },
                {
                    "field": "potential_concerns",
                    "question": "What are potential concerns or gaps for this Product Manager role?",
                    "type": "string"
                }
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=2)
        
        logger.info(f"✅ Example configuration created: {output_path}")
