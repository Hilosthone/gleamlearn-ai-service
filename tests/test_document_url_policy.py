"""SSRF protection for document downloads: only https URLs on allowed storage hosts, every redirect validated."""
import unittest
from unittest.mock import MagicMock, patch

from tests import _env  # noqa: F401  (sets dummy configuration before importing the app)

import dependencies
from fastapi import HTTPException


def response(status=200, location=None, body=b"%PDF-1.4", content_type="application/pdf"):
    r = MagicMock()
    r.__enter__.return_value = r
    r.is_redirect = location is not None
    r.headers = {"Content-Type": content_type, **({"Location": location} if location else {})}
    r.iter_content.return_value = [body]
    r.raise_for_status.return_value = None
    r.status_code = status
    return r


class DocumentUrlPolicyTests(unittest.TestCase):
    def test_allowed_cloudinary_url_passes(self):
        dependencies._validate_document_url("https://res.cloudinary.com/demo/raw/upload/doc.pdf")

    def test_disallowed_urls_are_rejected_without_any_request(self):
        bad = [
            "http://res.cloudinary.com/demo/doc.pdf",            # not https
            "https://169.254.169.254/latest/meta-data/",         # cloud metadata endpoint
            "https://127.0.0.1/doc.pdf",                         # loopback
            "https://internal.service.local/doc.pdf",            # arbitrary host
            "https://res.cloudinary.com.evil.test/doc.pdf",      # look-alike host
            "https://user:pass@res.cloudinary.com/doc.pdf",      # credentials in URL
            "https://res.cloudinary.com:8443/doc.pdf",           # unusual port
            "file:///etc/passwd",
            "not a url",
        ]
        with patch.object(dependencies.requests, "get") as get:
            for url in bad:
                with self.assertRaises(HTTPException, msg=url) as ctx:
                    dependencies._download_document(url)
                self.assertEqual(ctx.exception.status_code, 400, url)
            get.assert_not_called()

    def test_redirect_to_a_disallowed_host_is_refused(self):
        with patch.object(dependencies.requests, "get", return_value=response(302, "http://169.254.169.254/")) as get:
            with self.assertRaises(HTTPException) as ctx:
                dependencies._download_document("https://res.cloudinary.com/demo/doc.pdf")
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(get.call_count, 1)  # the redirect target was never requested
        self.assertFalse(get.call_args.kwargs["allow_redirects"])

    def test_redirect_within_allowed_hosts_is_followed(self):
        first = response(302, "/demo/doc-v2.pdf")
        second = response(200, body=b"%PDF-1.4 final")
        with patch.object(dependencies.requests, "get", side_effect=[first, second]) as get:
            data, content_type = dependencies._download_document("https://res.cloudinary.com/demo/doc.pdf")
        self.assertEqual(data, b"%PDF-1.4 final")
        self.assertEqual(content_type, "application/pdf")
        self.assertEqual(get.call_args_list[1].args[0], "https://res.cloudinary.com/demo/doc-v2.pdf")

    def test_redirect_loops_are_bounded(self):
        with patch.object(dependencies.requests, "get", side_effect=lambda *a, **k: response(302, "/again")) as get:
            with self.assertRaises(HTTPException):
                dependencies._download_document("https://res.cloudinary.com/demo/doc.pdf")
        self.assertEqual(get.call_count, dependencies.MAX_DOCUMENT_REDIRECTS + 1)

    def test_network_errors_do_not_echo_internal_details(self):
        with patch.object(dependencies.requests, "get", side_effect=ConnectionError("connect to 10.0.0.5:5432 refused")):
            with self.assertRaises(HTTPException) as ctx:
                dependencies._download_document("https://res.cloudinary.com/demo/doc.pdf")
        self.assertNotIn("10.0.0.5", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()
