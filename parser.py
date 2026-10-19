"""
Resume Parser Module.
Extracts raw text from PDF and DOCX files with defensive error handling,
and segments the extracted text into standard resume sections.
"""

import io
import re
from typing import Dict, Optional, Tuple
import pypdf
import docx


class ResumeParseError(Exception):
    """Custom exception raised when resume parsing fails."""
    pass


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extract text and page count from PDF bytes using pypdf.
    Handles encrypted or malformed PDFs gracefully.
    """
    try:
        pdf_stream = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_stream)
        
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise ResumeParseError("The uploaded PDF is password protected and cannot be read.")

        num_pages = len(reader.pages)
        if num_pages == 0:
            raise ResumeParseError("The PDF contains no pages.")

        extracted_text_list = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_text_list.append(page_text)

        full_text = "\n\n".join(extracted_text_list).strip()
        # Clean non-standard bullet artifacts
        full_text = re.sub(r"[\x7f\uf0b7\ufffd]", "• ", full_text)
        if not full_text:
            raise ResumeParseError(
                "Unable to extract text from PDF. It may be a scanned image or non-OCR document."
            )

        return full_text, num_pages

    except ResumeParseError:
        raise
    except Exception as e:
        raise ResumeParseError(f"Failed to parse PDF document: {str(e)}")


def extract_text_from_docx(file_bytes: bytes) -> Tuple[str, int]:
    """
    Extract text from DOCX bytes including paragraphs and table contents.
    """
    try:
        doc_stream = io.BytesIO(file_bytes)
        doc = docx.Document(doc_stream)
        
        full_text_list = []
        
        # 1. Paragraphs
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                full_text_list.append(text)
                
        # 2. Tables
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    full_text_list.append(" | ".join(row_cells))

        full_text = "\n".join(full_text_list).strip()
        full_text = re.sub(r"[\x7f\uf0b7\ufffd]", "• ", full_text)
        if not full_text:
            raise ResumeParseError("The DOCX document is empty or contains no readable text.")

        return full_text, 1  # DOCX has no strict page concept, default to 1

    except ResumeParseError:
        raise
    except Exception as e:
        raise ResumeParseError(f"Failed to parse DOCX document: {str(e)}")


def extract_text(file_bytes: bytes, file_name: str) -> Dict[str, any]:
    """
    Universal text extraction router based on file extension.
    Returns:
        {
            "success": bool,
            "text": str,
            "num_pages": int,
            "file_type": str,
            "error": str or None
        }
    """
    ext = file_name.lower().split(".")[-1] if "." in file_name else ""
    
    try:
        if ext == "pdf":
            text, pages = extract_text_from_pdf(file_bytes)
            return {
                "success": True,
                "text": text,
                "num_pages": pages,
                "file_type": "PDF",
                "error": None
            }
        elif ext in ["docx", "doc"]:
            text, pages = extract_text_from_docx(file_bytes)
            return {
                "success": True,
                "text": text,
                "num_pages": pages,
                "file_type": "DOCX",
                "error": None
            }
        elif ext == "txt":
            text = file_bytes.decode("utf-8", errors="replace").strip()
            if not text:
                raise ResumeParseError("Text file is empty.")
            return {
                "success": True,
                "text": text,
                "num_pages": 1,
                "file_type": "TXT",
                "error": None
            }
        else:
            raise ResumeParseError(f"Unsupported file format '.{ext}'. Please upload a PDF or DOCX file.")
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "num_pages": 0,
            "file_type": ext.upper(),
            "error": str(e)
        }


# Section identification regex patterns
SECTION_HEADERS = {
    "summary": re.compile(r"(summary|professional summary|executive summary|profile|about me|objective|career objective)", re.IGNORECASE),
    "experience": re.compile(r"(experience|work experience|professional experience|employment history|work history|relevant experience)", re.IGNORECASE),
    "education": re.compile(r"(education|academic background|academics|qualifications|academic qualification|degrees)", re.IGNORECASE),
    "skills": re.compile(r"(skills|technical skills|core competencies|competencies|technologies|proficiencies|tools & technologies)", re.IGNORECASE),
    "projects": re.compile(r"(projects|key projects|personal projects|academic projects|portfolio projects)", re.IGNORECASE),
    "certifications": re.compile(r"(certifications|certificates|licenses|courses|accreditations)", re.IGNORECASE),
    "awards": re.compile(r"(awards|honors|achievements|accomplishments)", re.IGNORECASE)
}


def segment_sections(text: str) -> Dict[str, str]:
    """
    Split resume text into logical sections based on common headings.
    Returns a dictionary of section_name -> section_content.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return {}

    sections: Dict[str, List[str]] = {
        "header": [],
        "summary": [],
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "certifications": [],
        "awards": [],
        "other": []
    }

    current_section = "header"

    for line in lines:
        # Check if line looks like a header (short, capitalized or bold/standalone)
        is_header = False
        if len(line) < 55 and not line.endswith((".", ",", ";")):
            for sec_key, pattern in SECTION_HEADERS.items():
                if pattern.fullmatch(line) or pattern.match(line):
                    current_section = sec_key
                    is_header = True
                    break

        if not is_header:
            sections[current_section].append(line)

    # Convert list of lines to joined string and prune empties
    result = {}
    for k, v in sections.items():
        joined = "\n".join(v).strip()
        if joined:
            result[k] = joined

    return result
