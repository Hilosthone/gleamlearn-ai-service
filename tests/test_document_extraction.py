import io
import unittest
import zipfile
from unittest.mock import AsyncMock, MagicMock, patch

from tests._env import TEST_AI_API_KEY

from fastapi import HTTPException
from fastapi.testclient import TestClient

import dependencies
import main
from types import SimpleNamespace


def make_pdf(text: str) -> bytes:
    """Builds a minimal one-page PDF with a single text line (no external tools needed)."""
    stream = f"BT /F1 24 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(out.tell())
        out.write(f"{i} 0 obj\n".encode() + body + b"\nendobj\n")
    xref = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for off in offsets:
        out.write(f"{off:010d} 00000 n \n".encode())
    out.write(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return out.getvalue()


def make_docx(paragraphs) -> bytes:
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
    xml = f'<?xml version="1.0"?><w:document xmlns:w="{ns}"><w:body>{body}</w:body></w:document>'
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr("word/document.xml", xml)
    return out.getvalue()


class ExtractDocumentTextTests(unittest.TestCase):
    def test_pdf_text_is_extracted_not_raw_bytes(self):
        text = dependencies.extract_document_text(make_pdf("Photosynthesis converts light"), "application/pdf")
        self.assertIn("Photosynthesis converts light", text)
        self.assertNotIn("%PDF", text)

    def test_pdf_detected_by_signature_even_with_generic_content_type(self):
        text = dependencies.extract_document_text(make_pdf("Cells divide"), "application/octet-stream")
        self.assertIn("Cells divide", text)

    def test_docx_text_is_extracted(self):
        text = dependencies.extract_document_text(make_docx(["First point", "Second point"]), "")
        self.assertEqual(text, "First point\nSecond point")

    def test_plain_text_passes_through_and_is_truncated(self):
        text = dependencies.extract_document_text(b"a" * 20000, "text/plain")
        self.assertEqual(len(text), dependencies.MAX_DOCUMENT_CHARS)

    def test_pdf_without_text_is_rejected(self):
        with self.assertRaises(HTTPException) as ctx:
            dependencies.extract_document_text(make_pdf(""), "application/pdf")
        self.assertEqual(ctx.exception.status_code, 422)

    def test_unsupported_binary_is_rejected(self):
        with self.assertRaises(HTTPException) as ctx:
            dependencies.extract_document_text(b"\x89PNG\r\n\x1a\n\x00\x00", "image/png")
        self.assertEqual(ctx.exception.status_code, 415)


class FetchPipelineTests(unittest.TestCase):
    def test_document_route_sends_extracted_pdf_text_to_model(self):
        fake_response = MagicMock()
        fake_response.__enter__.return_value = fake_response
        fake_response.headers = {"Content-Type": "application/pdf"}
        fake_response.iter_content.return_value = [make_pdf("Newton third law")]
        fake_response.raise_for_status.return_value = None

        create = AsyncMock(return_value=SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="summary"))]
        ))
        with patch.object(dependencies.requests, "get", return_value=fake_response), \
                patch.object(dependencies.client.chat.completions, "create", create):
            res = TestClient(main.app).post(
                "/api/v1/ai/documents/file-1/generate-summary",
                json={"fileId": "file-1", "fileUrl": "https://res.cloudinary.com/demo/doc.pdf", "options": {}},
                headers={"Authorization": f"Bearer {TEST_AI_API_KEY}"},
            )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["summary"], "summary")
        user_prompt = create.await_args.kwargs["messages"][1]["content"]
        self.assertIn("Newton third law", user_prompt)
        self.assertNotIn("%PDF", user_prompt)

    def test_oversized_download_is_rejected(self):
        fake_response = MagicMock()
        fake_response.__enter__.return_value = fake_response
        fake_response.headers = {"Content-Type": "application/pdf"}
        fake_response.iter_content.return_value = [b"x" * (dependencies.MAX_DOCUMENT_BYTES + 1)]
        with patch.object(dependencies.requests, "get", return_value=fake_response):
            with self.assertRaises(HTTPException) as ctx:
                dependencies._download_document("https://example.invalid/doc.pdf")
        self.assertEqual(ctx.exception.status_code, 413)


if __name__ == "__main__":
    unittest.main()
