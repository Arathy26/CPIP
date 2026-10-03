"""
Resume Parser Service

Deterministic (NOT LLM-based) extraction from an uploaded resume file.
Per CPIP's own Decision Boundary Guide — rules decide, LLM only assists —
this stays rule-based: extract real text, then use keyword/regex matching
to detect skills, contact info, degree, and role alignment. No guessing,
no fabrication. If something can't be confidently detected, it's left
None/empty rather than invented.

Supports: .pdf, .docx
Does NOT support: .doc (legacy binary Word format — would need extra
libraries; raises a clear error asking for .pdf or .docx instead)
"""

import io
import os
import re

from pypdf import PdfReader
from docx import Document
import pytesseract
from pdf2image import convert_from_bytes

# Windows needs explicit paths to these two programs unless they're on
# your system PATH. Set via .env — see setup instructions in the
# conversation where this file was built.
_TESSERACT_CMD = os.environ.get("TESSERACT_CMD_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
_POPPLER_PATH = os.environ.get("POPPLER_PATH")  # e.g. C:\poppler\Library\bin

if os.path.exists(_TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = _TESSERACT_CMD


class UnsupportedFileTypeError(Exception):
    pass


class OCRSetupError(Exception):
    pass


def _extract_text_via_ocr(file_bytes: bytes) -> str:
    """
    Fallback for PDFs with no real text layer — e.g. Canva/Claude Design
    exports where "text" is actually a rendered image, not real
    characters. Converts each page to an image, then uses Tesseract OCR
    to read the visible text out of that image.

    Slower and slightly less accurate than real text extraction, but
    works on ANY visual PDF, not just ones with an embedded text layer.
    """
    try:
        convert_kwargs = {"poppler_path": _POPPLER_PATH} if _POPPLER_PATH else {}
        images = convert_from_bytes(file_bytes, **convert_kwargs)
        return "\n".join(pytesseract.image_to_string(image) for image in images)
    except Exception as e:
        raise OCRSetupError(
            f"OCR fallback failed — check that Tesseract and Poppler are installed "
            f"and TESSERACT_CMD_PATH / POPPLER_PATH in your .env point to the right "
            f"folders. Underlying error: {e}"
        )


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Extracts raw text from an uploaded resume file's bytes."""
    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

        # If almost nothing came out, this PDF likely has no real text
        # layer at all. Fall back to OCR instead of giving up.
        if len(text.strip()) < 20:
            text = _extract_text_via_ocr(file_bytes)

        return text

    if lower_name.endswith(".docx"):
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)

    if lower_name.endswith(".doc"):
        raise UnsupportedFileTypeError(
            "Legacy .doc files aren't supported yet — please upload a .pdf or .docx instead."
        )

    raise UnsupportedFileTypeError(
        f"Unsupported file type for '{filename}'. Please upload a .pdf or .docx."
    )


_EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_PHONE_PATTERN = re.compile(r"(\+?\d[\d\-\s]{8,14}\d)")

_DEGREE_KEYWORDS = [
    "B.Tech", "B.E.", "BCA", "MCA", "M.Tech", "BBA", "MBA",
    "B.Sc", "M.Sc", "B.Com", "M.Com", "Bachelor", "Master",
]


def detect_email(text: str):
    match = _EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def detect_phone(text: str):
    match = _PHONE_PATTERN.search(text)
    return match.group(0).strip() if match else None


def detect_degree(text: str):
    lower_text = text.lower()
    for keyword in _DEGREE_KEYWORDS:
        if keyword.lower() in lower_text:
            return keyword
    return None


def detect_skills(text: str, known_skill_names):
    """
    Whole-skill, case-insensitive match against the skill vocabulary that
    recruiters have posted (seed_data.get_all_skill_names()). Deterministic:
    the same resume always gives the same skills. No LLM, no invented list.
    "C" does not match inside "React"; "Java" does not match "JavaScript".
    """
    lower_text = text.lower()
    found = []
    for skill in known_skill_names or []:
        name = str(skill).strip()
        if not name:
            continue
        pattern = r"(?<![a-z0-9+#.])" + re.escape(name.lower()) + r"(?![a-z0-9+#])"
        if re.search(pattern, lower_text):
            found.append(name)
    return found


_URL_PATTERN = re.compile(r"(https?://[^\s<>()\[\]\"',]+|www\.[^\s<>()\[\]\"',]+|(?:github|linkedin)\.com/[^\s<>()\[\]\"',]+)", re.IGNORECASE)


def detect_links(text: str):
    """GitHub / LinkedIn profile links written in the resume text."""
    urls = [u.rstrip(".;:") for u in _URL_PATTERN.findall(text or "")]
    def with_scheme(u):
        return u if u is None or u.lower().startswith(("http://", "https://")) else f"https://{u}"
    github = next((u for u in urls if "github.com" in u.lower()), None)
    linkedin = next((u for u in urls if "linkedin.com" in u.lower()), None)
    return {"github": with_scheme(github), "linkedin": with_scheme(linkedin)}


def detect_projects_section(text: str):
    """
    Very simple heuristic: does the resume mention "project" at all?
    This is deliberately basic and honest about being basic — it does
    NOT try to extract actual project titles (that would risk fabricating
    structure that isn't reliably there). Good enough to feed the
    Resume Readiness Agent's "is there a Projects section" checklist.
    """
    if re.search(r"\bproject", text, re.IGNORECASE):
        return ["Projects section detected in resume"]
    return []


def detect_role_alignment(text: str, target_role: str):
    if target_role and target_role.lower() in text.lower():
        return target_role
    return None


def detect_name(text: str):
    """
    Simple, honest heuristic: the candidate's name is almost always the
    first non-empty line of a resume. We guard against grabbing garbage
    (an email, a phone number, a long paragraph) by requiring the line
    to be short and free of @ / digits.

    Returns None if nothing reasonable is found — the caller should fall
    back to a plain label like "Candidate" rather than inventing a name.
    """
    for line in text.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        if len(candidate) > 60:
            continue
        if "@" in candidate or any(ch.isdigit() for ch in candidate):
            continue
        return candidate
    return None


def parse_resume(filename: str, file_bytes: bytes, target_role: str, known_skill_names):
    """
    Runs the full deterministic extraction pipeline.

    Returns a resume_data dict in exactly the shape resume_readiness_agent()
    expects:
    {
        "education": str|None, "skills": [str], "projects": [str],
        "contact": {"email": str|None, "phone": str|None},
        "role_alignment": str|None,
    }
    plus the raw extracted text (useful for debugging / future features).
    """
    text = extract_text(filename, file_bytes)

    return {
        "name": detect_name(text),
        "education": detect_degree(text),
        "skills": detect_skills(text, known_skill_names),
        "projects": detect_projects_section(text),
        "contact": {
            "email": detect_email(text),
            "phone": detect_phone(text),
        },
        "role_alignment": detect_role_alignment(text, target_role),
        "links": detect_links(text),
        "raw_text": text,  # NEW — needed by resume_readiness_agent for metrics/keyword checks
        "_raw_text_length": len(text),  # sanity-check signal, not shown to users
    }