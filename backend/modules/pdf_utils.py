from typing import Union
from PyPDF2 import PdfReader
import io


def extract_text_from_pdf(data: Union[bytes, io.BytesIO]) -> str:
    if isinstance(data, bytes):
        file_obj = io.BytesIO(data)
    else:
        file_obj = data
    reader = PdfReader(file_obj)
    text_parts = []
    for page in reader.pages:
        try:
            text_parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(text_parts)

