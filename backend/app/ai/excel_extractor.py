"""
AI-powered Excel data extraction for shipment proforma/invoice files.

This module uses Claude AI to intelligently extract fish shipment data
from Excel files in various formats.
"""

import pandas as pd
import io
from typing import Dict, List, Any, Optional
from fastapi import UploadFile

from app.ai.client import get_ai_client, get_default_model


def excel_to_text_representation(file_content: bytes, sheet_name: Optional[str] = None) -> str:
    """
    Convert Excel file to a text representation that AI can understand.

    Args:
        file_content: Raw Excel file bytes
        sheet_name: Optional specific sheet name to read

    Returns:
        Text representation of the Excel data
    """
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(io.BytesIO(file_content))

        # Get sheet names
        sheets = excel_file.sheet_names

        text_parts = []
        text_parts.append(f"Excel File with {len(sheets)} sheet(s): {', '.join(sheets)}\n")
        text_parts.append("=" * 80 + "\n")

        # Process specified sheet or all sheets
        sheets_to_process = [sheet_name] if sheet_name and sheet_name in sheets else sheets

        for sheet in sheets_to_process:
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet, header=None)

            text_parts.append(f"\n[SHEET: {sheet}]\n")
            text_parts.append("-" * 80 + "\n")

            # Convert dataframe to readable text format
            for idx, row in df.iterrows():
                # Skip completely empty rows
                if row.isna().all():
                    continue

                row_text = []
                for col_idx, value in enumerate(row):
                    if pd.notna(value):
                        row_text.append(f"Col{col_idx}: {value}")

                if row_text:
                    text_parts.append(f"Row {idx}: {' | '.join(row_text)}\n")

            text_parts.append("\n")

        return "".join(text_parts)

    except Exception as e:
        return f"Error reading Excel file: {str(e)}"


async def extract_shipment_data_from_excel(
    file: UploadFile,
    sheet_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use AI to extract shipment data from an Excel proforma/invoice.

    Args:
        file: Uploaded Excel file
        sheet_name: Optional specific sheet to analyze

    Returns:
        Dictionary with extracted shipment data
    """
    # Read file content
    file_content = await file.read()

    # Convert Excel to text
    excel_text = excel_to_text_representation(file_content, sheet_name)

    # Build AI prompt
    prompt = f"""You are analyzing a fish shipment proforma invoice or commercial invoice in Excel format.
Extract all relevant fish shipment information from this Excel file.

Excel Content:
{excel_text}

Please extract and structure the following information:

1. **Supplier Information:**
   - Supplier name
   - Source country

2. **Shipment Details:**
   - Shipment date (if available)
   - Expected arrival date (if available)
   - Invoice/Proforma number
   - Total boxes/packages

3. **Fish Species List:**
   For each fish species, extract:
   - Scientific name (Latin name, e.g., "Pterophyllum scalare")
   - Common name (if available)
   - Quantity (number of fish)
   - Size (if specified, e.g., "3-4cm", "adult", "juvenile")
   - Price per unit (if available)
   - Total price for this species (if available)

Return your response in this exact JSON format:
```json
{{
  "supplier_name": "supplier name or null",
  "source_country": "country name or null",
  "shipment_date": "YYYY-MM-DD or null",
  "expected_arrival": "YYYY-MM-DD or null",
  "invoice_number": "invoice/proforma number or null",
  "total_boxes": number or null,
  "fish_species": [
    {{
      "scientific_name": "Latin name",
      "common_name": "common name or null",
      "quantity": number,
      "size": "size description or null",
      "price_per_unit": number or null,
      "total_price": number or null,
      "notes": "any additional relevant info or null"
    }}
  ],
  "additional_notes": "any other important information from the invoice or null",
  "confidence": "high/medium/low - your confidence in the extraction"
}}
```

Important guidelines:
- Extract ALL fish species found in the document
- Use proper scientific names (Genus species format)
- If data is unclear or missing, use null
- Be careful with numbers - extract exact quantities
- Look for patterns like species lists, pricing tables, etc.
- The data might be in various formats - be flexible in identifying the information
"""

    # Call Claude API
    client = get_ai_client()

    try:
        response = client.messages.create(
            model=get_default_model(),
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        ai_text = response.content[0].text

        # Extract JSON from response (handle markdown code blocks)
        import json
        import re

        # Try to find JSON in markdown code block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', ai_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON directly
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("Could not find JSON in AI response")

        # Parse JSON
        extracted_data = json.loads(json_str)

        # Add metadata
        extracted_data["file_name"] = file.filename
        extracted_data["file_size"] = len(file_content)
        extracted_data["extraction_method"] = "ai_powered"

        return extracted_data

    except Exception as e:
        error_str = str(e)
        # Return user-friendly messages for known API errors
        if "overloaded_error" in error_str or "529" in error_str:
            user_message = "The AI service is temporarily overloaded. Please wait a moment and try again."
        elif "rate_limit" in error_str or "429" in error_str:
            user_message = "Rate limit reached. Please wait a minute and try again."
        elif "authentication" in error_str.lower() or "401" in error_str:
            user_message = "AI service authentication failed. Please check your API key."
        else:
            user_message = "AI extraction failed. Please try again."
        return {
            "error": user_message,
            "file_name": file.filename,
            "extraction_method": "failed"
        }


def validate_extracted_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate extracted shipment data and return any issues found.

    Args:
        data: Extracted data dictionary

    Returns:
        Dictionary with validation warnings and errors
    """
    warnings = []
    errors = []

    # Check required fields
    if not data.get("fish_species") or len(data.get("fish_species", [])) == 0:
        errors.append("No fish species found in the document")

    # Validate fish species data
    for idx, species in enumerate(data.get("fish_species", [])):
        species_name = species.get("scientific_name", "Unknown")

        if not species.get("scientific_name"):
            warnings.append(f"Species {idx + 1}: Missing scientific name")

        if not species.get("quantity") or species.get("quantity", 0) <= 0:
            warnings.append(f"{species_name}: Missing or invalid quantity")

        # Check scientific name format (should be at least two words)
        sci_name = species.get("scientific_name", "")
        if sci_name and len(sci_name.split()) < 2:
            warnings.append(f"{species_name}: Scientific name should be in 'Genus species' format")

    # Check supplier info
    if not data.get("supplier_name"):
        warnings.append("Supplier name not found")

    if not data.get("source_country"):
        warnings.append("Source country not found")

    return {
        "errors": errors,
        "warnings": warnings,
        "is_valid": len(errors) == 0
    }
