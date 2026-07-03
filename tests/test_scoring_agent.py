import sys
from pathlib import Path

# Add project root to path to allow importing agents package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.scoring_agent import (
    clean_domain,
    is_subdomain_of,
    is_sender_self_identified,
    check_lookalike,
    score_email,
)

# ---------------------------------------------------------------------------
# 1. Test clean_domain helper
# ---------------------------------------------------------------------------
def test_clean_domain_basic():
    assert clean_domain("www.google.com") == "google.com"
    assert clean_domain("  www.NETFLIX.com  ") == "netflix.com"

def test_clean_domain_no_corruption():
    # Verify lstrip fix (startswith www.) doesn't strip 'w' from words
    assert clean_domain("windows.example.com") == "windows.example.com"
    assert clean_domain("w.example.com") == "w.example.com"


# ---------------------------------------------------------------------------
# 2. Test is_subdomain_of helper
# ---------------------------------------------------------------------------
def test_is_subdomain_of():
    assert is_subdomain_of("google.com", "google.com") is True
    assert is_subdomain_of("accounts.google.com", "google.com") is True
    assert is_subdomain_of("myaccount.google.com", "google.com") is True
    assert is_subdomain_of("google.com.attacker.com", "google.com") is False


# ---------------------------------------------------------------------------
# 3. Test is_sender_self_identified helper
# ---------------------------------------------------------------------------
def test_is_sender_self_identified():
    assert is_sender_self_identified("Kaggle", "kaggle.com") is True
    assert is_sender_self_identified("TryHackMe", "tryhackme.com") is True
    assert is_sender_self_identified("Google Play", "google.com") is True
    assert is_sender_self_identified("PayPal Support", "hacker.com") is False
    assert is_sender_self_identified("", "google.com") is False


# ---------------------------------------------------------------------------
# 4. Test check_lookalike typosquatting check
# ---------------------------------------------------------------------------
def test_check_lookalike():
    assert check_lookalike("g00gle.com") == "google"
    assert check_lookalike("ch4se.com") == "chase"
    # Subdomains should not be flagged as lookalike
    assert check_lookalike("accounts.google.com") is None


# ---------------------------------------------------------------------------
# 5. Test score_email full runs
# ---------------------------------------------------------------------------
def test_score_email_cryptographic_bypass():
    # Verified Google security notice should get 0 score
    email = {
        "id": "sec-alert-test",
        "sender": "Google <no-reply@accounts.google.com>",
        "subject": "2-Step Verification turned on",
        "body_text": "2-Step Verification was enabled. Please review your settings.",
        "links": ["https://myaccount.google.com/security"],
        "headers": {
            "spf": "pass",
            "dkim": "pass",
            "dmarc": "pass"
        }
    }
    res = score_email(email)
    assert res["score"] == 0
    assert res["category"] == "safe"
    assert res["confidence"] == 1.0

def test_score_email_impersonation_phishing():
    # Spoofed netflix billing suspension
    email = {
        "id": "phish-test-netflix",
        "sender": "Netflix Alert <billing-update@customer-netfl1x-support.com>",
        "subject": "Your Netflix membership is about to be suspended",
        "body_text": "Please update your credentials immediately at http://bit.ly/netflix-suspend",
        "links": ["http://bit.ly/netflix-suspend"],
        "headers": {
            "spf": "fail",
            "dkim": "fail",
            "dmarc": "fail"
        }
    }
    res = score_email(email)
    assert res["score"] > 50
    assert res["category"] == "phishing"
    # Confidence is halved on attachments since there are no attachments
    assert res["confidence"] < 1.0

def test_score_email_scam_offer():
    # Lottery offer - no brand impersonation, but scam signals
    email = {
        "id": "scam-test",
        "sender": "Lottery Office <claims@freelotto-rewards.net>",
        "subject": "Congratulations! You won the $50,000 sweepstakes prize",
        "body_text": "Verify your identity and bank details to claim your free reward.",
        "links": [],
        "headers": {
            "spf": "pass",
            "dkim": "pass",
            "dmarc": "pass"
        }
    }
    res = score_email(email)
    assert res["category"] == "scam"
    assert res["score"] <= 50

def test_score_email_safe_mail():
    # Standard student communication
    email = {
        "id": "safe-test",
        "sender": "Professor <prof@state-university.edu>",
        "subject": "Project Extension Approved",
        "body_text": "Your extension request is approved. Submissions close next week.",
        "links": [],
        "headers": {
            "spf": "pass",
            "dkim": "pass",
            "dmarc": "pass"
        }
    }
    res = score_email(email)
    assert res["score"] == 0
    assert res["category"] == "safe"
