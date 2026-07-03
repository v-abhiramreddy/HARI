import sys
from pathlib import Path

# Add project root to path to allow importing agents package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.email_utils import (
    strip_html,
    decode_mime_header,
    extract_links,
    extract_auth_result,
)

# ---------------------------------------------------------------------------
def test_strip_html_basic():
    html = "<html><body><p>Hello <b>World</b>!</p></body></html>"
    assert strip_html(html) == "Hello World !"


def test_strip_html_skips_style_script():
    html = """
    <html>
      <head>
        <style>body { color: red; }</style>
        <script>console.log('hi');</script>
      </head>
      <body>
        <p>Visible Text</p>
      </body>
    </html>
    """
    assert strip_html(html) == "Visible Text"


# ---------------------------------------------------------------------------
# 2. Test decode_mime_header
# ---------------------------------------------------------------------------
def test_decode_mime_header_rfc2047():
    # Base64 encoded UTF-8 string: "Hello World"
    raw_b64 = "=?utf-8?B?SGVsbG8gV29ybGQ=?="
    assert decode_mime_header(raw_b64) == "Hello World"
    
    # Quoted-printable encoded: "Hello World"
    raw_qp = "=?utf-8?Q?Hello=20World?="
    assert decode_mime_header(raw_qp) == "Hello World"

def test_decode_mime_header_plain():
    assert decode_mime_header("Simple subject line") == "Simple subject line"
    assert decode_mime_header("") == ""


# ---------------------------------------------------------------------------
# 3. Test extract_links (URL link matching)
# ---------------------------------------------------------------------------
def test_extract_links_strips_punctuation():
    # Text with trailing periods, commas, parenthesis, and quotes
    text = (
        "Visit our portal at https://google.com/login. "
        "Or check http://chase.com/auth, or download "
        "https://netflix.com/sign-in) or 'https://paypal.com/verify'."
    )
    links = extract_links(text)
    
    # Verify matches are clean and trailing punctuation was removed
    assert "https://google.com/login" in links
    assert "http://chase.com/auth" in links
    assert "https://netflix.com/sign-in" in links
    assert "https://paypal.com/verify" in links
    
    # Verify no punctuation leaked into domains
    assert "https://google.com/login." not in links
    assert "http://chase.com/auth," not in links

def test_extract_links_deduplication():
    text = "Visit https://google.com or check https://google.com again."
    links = extract_links(text)
    assert len(links) == 1
    assert links[0] == "https://google.com"


# ---------------------------------------------------------------------------
# 4. Test extract_auth_result
# ---------------------------------------------------------------------------
def test_extract_auth_result():
    auth_header = (
        "mx.google.com; "
        "spf=pass (google.com: domain of support@google.com designates 209.85.220.41 as permitted sender) "
        "client-ip=209.85.220.41; "
        "dkim=pass header.i=@google.com header.s=20161025; "
        "dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=google.com"
    )
    assert extract_auth_result(auth_header, "spf") == "pass"
    assert extract_auth_result(auth_header, "dkim") == "pass"
    assert extract_auth_result(auth_header, "dmarc") == "pass"

def test_extract_auth_result_missing():
    auth_header = "spf=pass client-ip=1.2.3.4"
    assert extract_auth_result(auth_header, "dkim") == "none"
