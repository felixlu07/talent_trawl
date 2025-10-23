"""
Talent Trawler - Main Orchestrator

Scalable resume analysis system that processes PDF resumes using LLM vision models
and outputs structured data based on configurable criteria.

Usage:
    python talent_trawler.py <input_folder>
    
The input folder should contain:
    - PDF files (one per candidate)
    - config.json (job role and evaluation questions)
"""

import os
import sys
import logging
import csv
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from src.config_handler import ConfigHandler
from src.resume_processor import ResumeProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TalentTrawler:
    """Main orchestrator for resume processing pipeline"""
    
    def __init__(self, input_folder: str):
        """
        Initialize Talent Trawler
        
        Args:
            input_folder: Path to folder containing PDFs and config.json
        """
        self.input_folder = Path(input_folder)
        self.config = None
        self.processor = None
        
        # Validate input folder
        if not self.input_folder.exists():
            raise ValueError(f"Input folder does not exist: {input_folder}")
        
        if not self.input_folder.is_dir():
            raise ValueError(f"Input path is not a directory: {input_folder}")
    
    def run(self) -> None:
        """Execute the complete resume processing pipeline"""
        logger.info("\n" + "="*80)
        logger.info("🎯 TALENT TRAWLER - Resume Analysis System")
        logger.info("="*80)
        logger.info(f"📁 Input Folder: {self.input_folder.absolute()}")
        
        # Load environment variables
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
        
        if not api_key:
            logger.error("❌ ANTHROPIC_API_KEY not found in environment variables")
            logger.error("   Please set it in .env file or environment")
            return
        
        logger.info(f"🤖 Using model: {model}")
        
        # Load configuration
        config_path = self.input_folder / "config.json"
        self.config = ConfigHandler.load_config(str(config_path))
        
        if not self.config:
            logger.error("❌ Failed to load or validate configuration")
            logger.error(f"   Expected config file at: {config_path}")
            logger.info("\n💡 TIP: Run with --create-example to generate a sample config.json")
            return
        
        # Find PDF files
        pdf_files = self._find_pdf_files()
        
        if not pdf_files:
            logger.warning("⚠️  No PDF files found in input folder")
            return
        
        logger.info(f"\n📊 Found {len(pdf_files)} PDF file(s) to process")
        
        # Initialize processor
        self.processor = ResumeProcessor(api_key=api_key, model=model)
        
        # Process all resumes
        results = []
        successful = 0
        failed = 0
        
        for idx, pdf_path in enumerate(pdf_files, 1):
            logger.info(f"\n{'─'*80}")
            logger.info(f"Processing {idx}/{len(pdf_files)}")
            
            result = self.processor.process_resume(
                pdf_path=str(pdf_path),
                job_role=self.config["job_role"],
                questions=self.config["questions"]
            )
            
            results.append(result)
            
            if result.get("status") == "success":
                successful += 1
            else:
                failed += 1
        
        # Save results
        logger.info(f"\n{'='*80}")
        logger.info("💾 Saving Results")
        logger.info(f"{'='*80}")
        
        output_format = self.config.get("output_format", "csv").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create descriptive filename: resume_trawl_<count>_resumes_<timestamp>
        filename = f"resume_trawl_{len(pdf_files)}_resumes_{timestamp}"
        
        if output_format == "csv":
            output_file = self.input_folder / f"{filename}.csv"
            self._save_as_csv(results, output_file)
        else:
            output_file = self.input_folder / f"{filename}.json"
            self._save_as_json(results, output_file)
        
        # Calculate total cost
        total_cost = sum(r.get("cost_usd", 0.0) for r in results)
        total_input_tokens = sum(r.get("input_tokens", 0) for r in results)
        total_output_tokens = sum(r.get("output_tokens", 0) for r in results)
        avg_cost_per_resume = total_cost / len(pdf_files) if pdf_files else 0
        
        # Summary
        logger.info(f"\n{'='*80}")
        logger.info("📈 PROCESSING SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total PDFs: {len(pdf_files)}")
        logger.info(f"✅ Successful: {successful}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"💰 Total Cost: ${total_cost:.4f} USD")
        logger.info(f"💵 Avg Cost/Resume: ${avg_cost_per_resume:.4f} USD")
        logger.info(f"🔢 Total Tokens: {total_input_tokens:,} in / {total_output_tokens:,} out")
        logger.info(f"📄 Output: {output_file.absolute()}")
        logger.info(f"{'='*80}\n")
    
    def _find_pdf_files(self) -> List[Path]:
        """
        Find all PDF files in the input folder
        
        Returns:
            List of Path objects for PDF files
        """
        pdf_files = list(self.input_folder.glob("*.pdf"))
        pdf_files.extend(self.input_folder.glob("*.PDF"))
        
        # Remove duplicates and sort
        pdf_files = sorted(set(pdf_files))
        
        for pdf in pdf_files:
            logger.info(f"  📄 {pdf.name} ({pdf.stat().st_size:,} bytes)")
        
        return pdf_files
    
    def _save_as_csv(self, results: List[Dict[str, Any]], output_file: Path) -> None:
        """
        Save results as CSV file
        
        Args:
            results: List of result dictionaries
            output_file: Path to output CSV file
        """
        if not results:
            logger.warning("⚠️  No results to save")
            return
        
        # Determine all field names
        fieldnames = ["filename", "status", "pages_processed", "input_tokens", "output_tokens", "cost_usd"]
        
        # Add question fields
        for question in self.config["questions"]:
            fieldnames.append(question["field"])
        
        # Add error field if any errors exist
        if any(r.get("status") == "error" for r in results):
            fieldnames.append("error")
        
        # Write CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                # Create row with all fields
                row = {field: result.get(field, "") for field in fieldnames}
                writer.writerow(row)
        
        # Calculate total cost
        total_cost = sum(r.get("cost_usd", 0.0) for r in results)
        total_input_tokens = sum(r.get("input_tokens", 0) for r in results)
        total_output_tokens = sum(r.get("output_tokens", 0) for r in results)
        
        logger.info(f"✅ CSV saved: {output_file}")
        logger.info(f"   Rows: {len(results)}")
        logger.info(f"   Columns: {len(fieldnames)}")
        logger.info(f"   Total Cost: ${total_cost:.4f} USD")
        logger.info(f"   Total Tokens: {total_input_tokens:,} in / {total_output_tokens:,} out")
    
    def _save_as_json(self, results: List[Dict[str, Any]], output_file: Path) -> None:
        """
        Save results as JSON file
        
        Args:
            results: List of result dictionaries
            output_file: Path to output JSON file
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"✅ JSON saved: {output_file}")
        logger.info(f"   Records: {len(results)}")


def create_example_config(folder_path: str) -> None:
    """
    Create an example config.json in the specified folder
    
    Args:
        folder_path: Path to folder where config should be created
    """
    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)
    
    config_path = folder / "config.json"
    
    if config_path.exists():
        logger.warning(f"⚠️  Config file already exists: {config_path}")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            logger.info("Cancelled")
            return
    
    ConfigHandler.create_example_config(str(config_path))
    logger.info(f"\n✅ Example configuration created at: {config_path}")
    logger.info("\n📝 Next steps:")
    logger.info("   1. Review and customize config.json for your needs")
    logger.info("   2. Add PDF resumes to the folder")
    logger.info(f"   3. Run: python talent_trawler.py {folder_path}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python talent_trawler.py <input_folder>")
        print("   or: python talent_trawler.py --create-example <folder>")
        print("\nThe input folder should contain:")
        print("  - PDF files (one per candidate)")
        print("  - config.json (job role and evaluation questions)")
        sys.exit(1)
    
    # Check for example creation flag
    if sys.argv[1] == "--create-example":
        if len(sys.argv) < 3:
            print("Usage: python talent_trawler.py --create-example <folder>")
            sys.exit(1)
        create_example_config(sys.argv[2])
        return
    
    # Normal processing
    input_folder = sys.argv[1]
    
    try:
        trawler = TalentTrawler(input_folder)
        trawler.run()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
