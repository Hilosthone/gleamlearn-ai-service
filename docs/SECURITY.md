# Security

- **Service authentication:**
  - Every route requires `AI_API_KEY`. The comparison uses `hmac.compare_digest` (`_matches_key`), so it is constant-time.
  - Startup fails without the key, and there are no fallback values.
  - **The old key is in the public git history** (`bb99205`). Until it is rotated, anyone can call this service directly.
- **SSRF protection (Batch 7)** for documents:
  - Downloads only `https://` URLs on `ALLOWED_DOCUMENT_HOSTS` (default `res.cloudinary.com`), with no credentials and only port 443.
  - Redirects are followed **manually**: at most 3, and each one is validated.
  - Failure messages are generic, so internal hosts can't be probed through error text.
  - Covered by `tests/test_document_url_policy.py` (6 tests) and verified live.
  - The backend independently forwards only its own Cloudinary URLs (`CLOUDINARY_CLOUD_NAME`), which gives two layers.
- **Secrets:** there are no keys in code. Commented-out legacy code still contains placeholder strings (`674930`, `your_secret_token`) that are inert; deleting them is cosmetic.
- **Open:** a provider error's text is included in the 502 detail sent to the backend. The backend doesn't forward it, so this is low risk, but making it generic here too is a small follow-up.
