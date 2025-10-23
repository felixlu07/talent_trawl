# Talent Trawler 🎯

```
                 __/___
           _____/______|
   _______/_____\_______\_____
   \              &lt; &lt; &lt;|
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

Ever had to review 150 resumes while desperately needing a bathroom break? Yeah, me too. That's why I built Talent Trawler - so you can process resumes at machine speed and actually enjoy your evening with a glass of wine.

**AI-powered resume screening that processes hundreds of CVs in minutes, not days.**

Talent Trawler uses Claude's vision model to read PDF resumes directly and extract structured data based on your custom criteria. Perfect for recruiters, hiring managers, and HR teams drowning in applications.

## Features

- **Batch Processing**: Analyze 100+ resumes efficiently
- **Flexible Configuration**: Define custom evaluation criteria via JSON
- **Vision-Based Analysis**: Direct PDF reading using Claude's vision model
- **Cost Tracking**: Per-resume and total cost calculation
- **Structured Output**: CSV/JSON format with clean, sanitized data
- **Type-Safe Extraction**: Define field types (string, int, float, bool)
- **AI-Powered Scoring**: Configurable candidate evaluation and ranking

## Quick Start

### 1. Prerequisites

**Poppler** (required for PDF processing):

**Windows:**
- Download: https://github.com/oschwartz10612/poppler-windows/releases/
- Extract to `C:\Program Files\poppler-XX.XX.X\`
- System auto-detects common installation paths
- **Custom location?** Set `POPPLER_PATH` in `.env` (see step 3)

**Mac:**
```bash
brew install poppler
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# Fedora
sudo dnf install poppler-utils
```

**Note:** Linux/Mac users typically don't need additional configuration as Poppler is auto-detected from system PATH.

### 2. Setup

**Windows:**
```powershell
.\scripts\setup.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/setup.sh scripts/run.sh
./scripts/setup.sh
```

**Manual setup (all platforms):**
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure API Key

Copy `.env.example` to `.env` and add your API key:
```
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# Optional: Only if Poppler is in a custom location
# POPPLER_PATH=C:\Program Files\poppler-24.08.0\Library\bin
```

### 4. Create Configuration

```powershell
python talent_trawler.py --create-example pm_candidates
```

This creates a folder with example `config.json` for Product Manager role.

### 5. Add Resumes and Run

```bash
# Add PDF files to pm_candidates/ folder

# Windows
python talent_trawler.py pm_candidates
# or use helper: .\scripts\run.ps1 pm_candidates

# Linux/Mac
python3 talent_trawler.py pm_candidates
# or use helper: ./scripts/run.sh pm_candidates
```

## Configuration Format

Each input folder needs a `config.json` file:

```json
{
  "job_role": "Product Manager",
  "output_format": "csv",
  "questions": [
    {
      "field": "candidate_name",
      "question": "What is the candidate's full name?",
      "type": "string"
    },
    {
      "field": "total_years_experience",
      "question": "How many total years of professional experience?",
      "type": "float"
    },
    {
      "field": "number_of_jobs",
      "question": "How many different jobs has the candidate held?",
      "type": "int"
    }
  ]
}
```

### Field Types

- `string`: Text data
- `int`: Whole numbers
- `float`: Decimal numbers
- `bool`: True/False values

## Output

Results are saved as: `resume_trawl_N_resumes_TIMESTAMP.csv`

Example: `resume_trawl_100_resumes_20251023_143052.csv`

### CSV Columns
- `filename`: PDF filename
- `status`: success/error
- `pages_processed`: Number of pages analyzed
- `input_tokens`, `output_tokens`, `cost_usd`: Cost tracking
- Custom fields from your configuration
- `error`: Error message (if failed)

### Cost Information
- **Pricing**: $3/M input tokens, $15/M output tokens
- **Per-resume cost**: Displayed in logs and CSV
- **Total cost**: Shown in processing summary

## Example Use Cases

### Evaluate Product Manager Candidates
- Years of PM experience
- Team size managed
- Product launch track record
- Technical background

### Screen Software Engineers
- Programming languages
- Years of experience per language
- Education background
- Open source contributions

### Assess Sales Professionals
- Years in sales
- Industries worked in
- Quota achievement history
- Team leadership experience

## Logging

The system provides detailed logging:
- ✅ Success indicators
- ❌ Error markers
- 📄 PDF processing stats
- 🔍 Image validation results
- 🤖 LLM analysis progress

## Error Handling

- Invalid PDFs are logged and skipped
- Failed image conversions are reported
- API errors are captured with details
- Partial results are still saved

## Best Practices

1. **Test First**: Run on 2-3 resumes before batch processing
2. **Clear Questions**: Be specific in your evaluation questions
3. **Appropriate Types**: Use correct data types for accurate analysis
4. **Monitor Logs**: Watch for validation warnings
5. **Review Output**: Spot-check results for accuracy

## Troubleshooting

**"PDF file not found"**
- Ensure PDFs are in the input folder
- Check file extensions (.pdf or .PDF)

**"Failed to convert PDF to images"**
- Verify Poppler is installed correctly
- **Windows:** Check if auto-detection found Poppler (look for log message)
- **Custom installation:** Set `POPPLER_PATH` in `.env` to your Poppler bin directory
- Check PDF is not corrupted or password-protected

**"API error"**
- Verify ANTHROPIC_API_KEY in .env
- Check API quota/limits

**Empty results**
- Review LLM response in logs
- Ensure questions are clear
- Check PDF quality/readability

## Project Structure

```
talent_trawler/
├── src/
│   ├── config_handler.py      # Configuration validation
│   ├── resume_processor.py    # Core processing logic
│   └── utils/
│       └── pdf_helper.py      # PDF/image utilities
├── scripts/
│   ├── setup.ps1              # Automated setup
│   └── run.ps1                # Quick run helper
├── talent_trawler.py          # Main entry point
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## Data Flow

1. **Input**: Folder with PDFs + `config.json`
2. **PDF → Images**: Convert using Poppler
3. **LLM Analysis**: Send images to Claude vision model
4. **Parse & Sanitize**: Extract structured data, clean special characters
5. **Output**: Single CSV with all resumes + cost tracking

## Scripts

### Setup Scripts
**Windows:** `scripts/setup.ps1`  
**Linux/Mac:** `scripts/setup.sh`

Automated setup that:
- Creates virtual environment
- Installs dependencies
- Copies `.env.example` to `.env`
- Validates Poppler installation

### Run Helpers
**Windows:**
```powershell
.\scripts\run.ps1 pm_candidates
```

**Linux/Mac:**
```bash
./scripts/run.sh pm_candidates
```

## License

MIT
