# feature1.py
"""
FeatureExtraction for phishing detection.

Behavior:
- If a dataset file named 'dataset_cybersecurity_michelle.csv' exists in cwd,
  the module will read the header to determine the expected feature order
  (excluding the label 'phishing') and return features in that order.
- Otherwise uses a safe default order (URL/domain-based features + placeholders).
- All features return numeric values. Network/WHOIS/SSL lookups use safe fallbacks.
- Raises ValueError on malformed URL (you can catch and treat as phishing).
"""

import re
from urllib.parse import urlparse
import ipaddress
import requests
from bs4 import BeautifulSoup
import whois
from datetime import datetime
import os
import csv

# -----------------------------
# Helper utilities
# -----------------------------
def safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default

def safe_float(x, default=-1.0):
    try:
        return float(x)
    except Exception:
        return default

def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            add = prev[j] + 1
            delete = cur[j - 1] + 1
            change = prev[j - 1] + (0 if ca == cb else 1)
            cur[j] = min(add, delete, change)
        prev = cur
    return prev[-1]

# Brands and heuristics lists (extend as needed)
BRAND_LIST = ["google", "paypal", "facebook", "microsoft", "amazon", "youtube", "bankofamerica", "github"]
LOGIN_KEYWORDS = ["login", "secure", "verify", "account", "update", "signin", "auth", "secure-login"]
SUSPICIOUS_TLDS = {".info", ".xyz", ".pw", ".top", ".club", ".online", ".site", ".biz"}

# -----------------------------
# Determine expected feature order
# -----------------------------
def _read_feature_order_from_csv(csv_path="dataset_cybersecurity_michelle.csv", label_col="phishing"):
    """
    Try to read header from dataset CSV and return a list of feature names excluding label.
    If file not found or parse fails, return None.
    """
    if not os.path.exists(csv_path):
        return None
    try:
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            # remove label if present
            feature_names = [h for h in header if h != label_col]
            return feature_names
    except Exception:
        return None

# Attempt to detect feature order from dataset
DETECTED_FEATURE_ORDER = _read_feature_order_from_csv()

# Provide a fallback default order (common subset + placeholders)
FALLBACK_FEATURE_ORDER = [
    # URL-level (some common ones)
    "qty_dot_url","qty_hyphen_url","qty_underline_url","qty_slash_url","qty_questionmark_url",
    "qty_equal_url","qty_at_url","qty_and_url","qty_exclamation_url","qty_space_url",
    "qty_tilde_url","qty_comma_url","qty_plus_url","qty_asterisk_url","qty_hashtag_url",
    "qty_dollar_url","qty_percent_url","qty_tld_url","length_url",
    # Domain-level (some common)
    "qty_dot_domain","qty_hyphen_domain","qty_underline_domain","qty_slash_domain","qty_questionmark_domain",
    "qty_equal_domain","qty_at_domain","qty_and_domain","qty_exclamation_domain","qty_space_domain",
    "qty_tilde_domain","qty_comma_domain","qty_plus_domain","qty_asterisk_domain","qty_hashtag_domain",
    "qty_dollar_domain","qty_percent_domain","qty_vowels_domain","domain_length","domain_in_ip",
    "server_client_domain",
    # Directory/file/params (some)
    "qty_dot_directory","qty_hyphen_directory","qty_underline_directory","qty_slash_directory","qty_questionmark_directory",
    "qty_equal_directory","qty_at_directory","qty_and_directory","qty_exclamation_directory","qty_space_directory",
    "qty_tilde_directory","qty_comma_directory","qty_plus_directory","qty_asterisk_directory","qty_hashtag_directory",
    "qty_dollar_directory","qty_percent_directory","directory_length",
    "qty_dot_file","qty_hyphen_file","qty_underline_file","qty_slash_file","qty_questionmark_file",
    "qty_equal_file","qty_at_file","qty_and_file","qty_exclamation_file","qty_space_file",
    "qty_tilde_file","qty_comma_file","qty_plus_file","qty_asterisk_file","qty_hashtag_file",
    "qty_dollar_file","qty_percent_file","file_length",
    "qty_dot_params","qty_hyphen_params","qty_underline_params","qty_slash_params","qty_questionmark_params",
    "qty_equal_params","qty_at_params","qty_and_params","qty_exclamation_params","qty_space_params",
    "qty_tilde_params","qty_comma_params","qty_plus_params","qty_asterisk_params","qty_hashtag_params",
    "qty_dollar_params","qty_percent_params","params_length","tld_present_params","qty_params",
    "email_in_url",
    # Network / timing / DNS / WHOIS placeholders
    "time_response","domain_spf","asn_ip","time_domain_activation","time_domain_expiration",
    "qty_ip_resolved","qty_nameservers","qty_mx_servers","ttl_hostname","tls_ssl_certificate",
    "qty_redirects","url_google_index","domain_google_index","url_shortened",
    # Heuristic features (added)
    "heuristic_brand_flag","heuristic_typo_score_min","heuristic_brand_as_subdomain","heuristic_login_words",
    "heuristic_suspicious_tld"
]

# Choose final feature order
FEATURE_ORDER = DETECTED_FEATURE_ORDER if DETECTED_FEATURE_ORDER is not None else FALLBACK_FEATURE_ORDER

# -----------------------------
# FeatureExtraction Class
# -----------------------------
class FeatureExtraction:
    def __init__(self, url):
        self.url = (url or "").strip()
        self.domain = ""
        self.urlparse_response = None
        self.response = None
        self.soup = None
        self.whois_response = None

        # Validate URL
        if not self.is_valid_url(self.url):
            raise ValueError(f"Invalid URL format: {self.url}")

        # Parse URL
        try:
            self.urlparse_response = urlparse(self.url)
            self.domain = (self.urlparse_response.netloc or "").lower()
            # remove port if any
            if ":" in self.domain:
                self.domain = self.domain.split(":")[0]
        except Exception:
            self.domain = ""

        # Fetch WHOIS (safe)
        try:
            if self.domain:
                self.whois_response = whois.whois(self.domain)
        except Exception:
            self.whois_response = None

        # Fetch content (safe)
        try:
            self.response = requests.get(self.url, timeout=5)
            self.soup = BeautifulSoup(self.response.text, "html.parser")
        except Exception:
            self.response = None
            self.soup = None

        # Precompute lower-case host and path for fast checks
        self._host = (self.domain or "").lower()
        self._path = (self.urlparse_response.path or "").lower() if self.urlparse_response else ""
        self._query = (self.urlparse_response.query or "").lower() if self.urlparse_response else ""

    # -------------------------
    # Basic helpers / counters
    # -------------------------
    @staticmethod
    def is_valid_url(url):
        try:
            result = urlparse(url)
            return result.scheme in ("http", "https") and bool(result.netloc)
        except Exception:
            return False

    def count_char(self, ch, text):
        if not isinstance(text, str):
            return 0
        return text.count(ch)

    # -------------------------
    # URL-level features
    # -------------------------
    def qty_dot_url(self): return self.count_char('.', self.url)
    def qty_hyphen_url(self): return self.count_char('-', self.url)
    def qty_underline_url(self): return self.count_char('_', self.url)
    def qty_slash_url(self): return self.count_char('/', self.url)
    def qty_questionmark_url(self): return self.count_char('?', self.url)
    def qty_equal_url(self): return self.count_char('=', self.url)
    def qty_at_url(self): return self.count_char('@', self.url)
    def qty_and_url(self): return self.count_char('&', self.url)
    def qty_exclamation_url(self): return self.count_char('!', self.url)
    def qty_space_url(self): return self.count_char(' ', self.url)
    def qty_tilde_url(self): return self.count_char('~', self.url)
    def qty_comma_url(self): return self.count_char(',', self.url)
    def qty_plus_url(self): return self.count_char('+', self.url)
    def qty_asterisk_url(self): return self.count_char('*', self.url)
    def qty_hashtag_url(self): return self.count_char('#', self.url)
    def qty_dollar_url(self): return self.count_char('$', self.url)
    def qty_percent_url(self): return self.count_char('%', self.url)
    def qty_tld_url(self):
        if not self.domain:
            return 0
        return len(re.findall(r'\.[a-zA-Z]{2,}', self.domain))
    def length_url(self): return len(self.url) if self.url else 0

    # -------------------------
    # Domain-level features
    # -------------------------
    def qty_dot_domain(self): return self.count_char('.', self.domain)
    def qty_hyphen_domain(self): return self.count_char('-', self.domain)
    def qty_underline_domain(self): return self.count_char('_', self.domain)
    def qty_slash_domain(self): return self.count_char('/', self.domain)
    def qty_questionmark_domain(self): return self.count_char('?', self.domain)
    def qty_equal_domain(self): return self.count_char('=', self.domain)
    def qty_at_domain(self): return self.count_char('@', self.domain)
    def qty_and_domain(self): return self.count_char('&', self.domain)
    def qty_exclamation_domain(self): return self.count_char('!', self.domain)
    def qty_space_domain(self): return self.count_char(' ', self.domain)
    def qty_tilde_domain(self): return self.count_char('~', self.domain)
    def qty_comma_domain(self): return self.count_char(',', self.domain)
    def qty_plus_domain(self): return self.count_char('+', self.domain)
    def qty_asterisk_domain(self): return self.count_char('*', self.domain)
    def qty_hashtag_domain(self): return self.count_char('#', self.domain)
    def qty_dollar_domain(self): return self.count_char('$', self.domain)
    def qty_percent_domain(self): return self.count_char('%', self.domain)
    def qty_vowels_domain(self):
        if not self.domain:
            return 0
        return len(re.findall(r'[aeiou]', self.domain.lower()))
    def domain_length(self): return len(self.domain) if self.domain else 0
    def domain_in_ip(self):
        try:
            ipaddress.ip_address(self.domain)
            return 1
        except Exception:
            return 0
    def server_client_domain(self):
        # Placeholder (requires network/system heuristics)
        return 0

    # -------------------------
    # Directory / file / params
    # -------------------------
    def qty_dot_directory(self): return self.count_char('.', self._path)
    def qty_hyphen_directory(self): return self.count_char('-', self._path)
    def qty_underline_directory(self): return self.count_char('_', self._path)
    def qty_slash_directory(self): return self.count_char('/', self._path)
    def qty_questionmark_directory(self): return self.count_char('?', self._path)
    def qty_equal_directory(self): return self.count_char('=', self._path)
    def qty_at_directory(self): return self.count_char('@', self._path)
    def qty_and_directory(self): return self.count_char('&', self._path)
    def qty_exclamation_directory(self): return self.count_char('!', self._path)
    def qty_space_directory(self): return self.count_char(' ', self._path)
    def qty_tilde_directory(self): return self.count_char('~', self._path)
    def qty_comma_directory(self): return self.count_char(',', self._path)
    def qty_plus_directory(self): return self.count_char('+', self._path)
    def qty_asterisk_directory(self): return self.count_char('*', self._path)
    def qty_hashtag_directory(self): return self.count_char('#', self._path)
    def qty_dollar_directory(self): return self.count_char('$', self._path)
    def qty_percent_directory(self): return self.count_char('%', self._path)
    def directory_length(self):
        return len(self._path) if isinstance(self._path, str) else -1

    def get_file(self):
        if not self.urlparse_response or not self.urlparse_response.path:
            return ""
        return self.urlparse_response.path.split('/')[-1]

    def qty_dot_file(self): return self.count_char('.', self.get_file())
    def qty_hyphen_file(self): return self.count_char('-', self.get_file())
    def qty_underline_file(self): return self.count_char('_', self.get_file())
    def qty_slash_file(self): return self.count_char('/', self.get_file())
    def qty_questionmark_file(self): return self.count_char('?', self.get_file())
    def qty_equal_file(self): return self.count_char('=', self.get_file())
    def qty_at_file(self): return self.count_char('@', self.get_file())
    def qty_and_file(self): return self.count_char('&', self.get_file())
    def qty_exclamation_file(self): return self.count_char('!', self.get_file())
    def qty_space_file(self): return self.count_char(' ', self.get_file())
    def qty_tilde_file(self): return self.count_char('~', self.get_file())
    def qty_comma_file(self): return self.count_char(',', self.get_file())
    def qty_plus_file(self): return self.count_char('+', self.get_file())
    def qty_asterisk_file(self): return self.count_char('*', self.get_file())
    def qty_hashtag_file(self): return self.count_char('#', self.get_file())
    def qty_dollar_file(self): return self.count_char('$', self.get_file())
    def qty_percent_file(self): return self.count_char('%', self.get_file())
    def file_length(self): return len(self.get_file()) if self.get_file() else -1

    def qty_dot_params(self): return self.count_char('.', self._query)
    def qty_hyphen_params(self): return self.count_char('-', self._query)
    def qty_underline_params(self): return self.count_char('_', self._query)
    def qty_slash_params(self): return self.count_char('/', self._query)
    def qty_questionmark_params(self): return self.count_char('?', self._query)
    def qty_equal_params(self): return self.count_char('=', self._query)
    def qty_at_params(self): return self.count_char('@', self._query)
    def qty_and_params(self): return self.count_char('&', self._query)
    def qty_exclamation_params(self): return self.count_char('!', self._query)
    def qty_space_params(self): return self.count_char(' ', self._query)
    def qty_tilde_params(self): return self.count_char('~', self._query)
    def qty_comma_params(self): return self.count_char(',', self._query)
    def qty_plus_params(self): return self.count_char('+', self._query)
    def qty_asterisk_params(self): return self.count_char('*', self._query)
    def qty_hashtag_params(self): return self.count_char('#', self._query)
    def qty_dollar_params(self): return self.count_char('$', self._query)
    def qty_percent_params(self): return self.count_char('%', self._query)
    def params_length(self): return len(self._query) if self._query else -1
    def tld_present_params(self):
        # Placeholder; complex to compute without TLD list
        return -1
    def qty_params(self):
        if not self._query:
            return -1
        return len([p for p in self._query.split("&") if p.strip()])

    def email_in_url(self): return 1 if self.count_char('@', self.url) > 0 else 0

    # -------------------------
    # Network / WHOIS / DNS / SSL placeholders
    # -------------------------
    def time_response(self): return self.response.elapsed.total_seconds() if self.response else -1
    def domain_spf(self):
        # Placeholder - needs DNS TXT lookup
        return -1
    def asn_ip(self):
        # Placeholder - requires external service
        return -1
    def time_domain_activation(self):
        # Attempt to get from whois if available
        try:
            if self.whois_response and hasattr(self.whois_response, "creation_date") and self.whois_response.creation_date:
                cd = self.whois_response.creation_date
                if isinstance(cd, list):
                    cd = cd[0]
                if isinstance(cd, datetime):
                    return (datetime.now() - cd).days
        except Exception:
            pass
        return -1
    def time_domain_expiration(self):
        try:
            if self.whois_response and hasattr(self.whois_response, "expiration_date") and self.whois_response.expiration_date:
                ed = self.whois_response.expiration_date
                if isinstance(ed, list):
                    ed = ed[0]
                if isinstance(ed, datetime):
                    return (ed - datetime.now()).days
        except Exception:
            pass
        return -1
    def qty_ip_resolved(self):
        try:
            if not self.domain:
                return -1
            import socket
            ips = socket.gethostbyname_ex(self.domain)[2]
            return len(ips)
        except Exception:
            return -1
    def qty_nameservers(self):
        # Placeholder - requires DNS NS query
        return -1
    def qty_mx_servers(self):
        # Placeholder - requires DNS MX query
        return -1
    def ttl_hostname(self):
        # Placeholder
        return -1
    def tls_ssl_certificate(self):
        # Very basic: if response and response.url starts with https -> 1
        try:
            return 1 if self.urlparse_response.scheme == "https" else 0
        except Exception:
            return -1
    def qty_redirects(self):
        return len(self.response.history) if self.response else -1
    def url_google_index(self):
        # Placeholder (requires search engine API)
        return 0
    def domain_google_index(self):
        # Placeholder
        return 0
    def url_shortened(self):
        # Very naive check for common URL shorteners
        shorteners = ("bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd")
        try:
            return 1 if any(s in self._host for s in shorteners) else 0
        except Exception:
            return 0

    # -------------------------
    # Heuristic helpers (brand/typo/subdomain/login-word/tld)
    # -------------------------
    def get_registered_domain(self):
        netloc = (self.domain or "").split(':')[0].lower()
        parts = [p for p in netloc.split('.') if p]
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return netloc

    def brand_typo_score(self, brand):
        sld = self.get_registered_domain().split('.')[0] if self.get_registered_domain() else ""
        return levenshtein(sld, brand)

    def contains_brand_token(self):
        host = (self.domain or "").lower()
        for brand in BRAND_LIST:
            if brand in host:
                return brand
        return None

    def brand_as_subdomain(self):
        host = (self.domain or "").lower()
        for brand in BRAND_LIST:
            pattern = rf"{re.escape(brand)}\.(com|net|org|co|in|uk)\."
            if re.search(pattern, host):
                return True
        return False

    def suspicious_tld(self):
        reg = self.get_registered_domain().lower()
        for t in SUSPICIOUS_TLDS:
            if reg.endswith(t):
                return True
        return False

    def contains_login_words(self):
        host = (self.domain or "").lower()
        if any(kw in host for kw in LOGIN_KEYWORDS):
            return True
        if any(kw in self._path for kw in LOGIN_KEYWORDS):
            return True
        return False

    def heuristic_is_phishing(self):
        reasons = []
        brand = self.contains_brand_token()
        if brand:
            reg = self.get_registered_domain().lower()
            if reg != f"{brand}.com":
                reasons.append(f"brand_token_in_host:{brand}")
            score = self.brand_typo_score(brand)
            if score <= 2 and score != 0:
                reasons.append(f"typo_squatting:{brand}:dist={score}")
        if self.brand_as_subdomain():
            reasons.append("brand_as_subdomain_trick")
        if brand and self.contains_login_words():
            reasons.append("brand_plus_login_words")
        if self.suspicious_tld():
            reasons.append("suspicious_tld")
        return (len(reasons) > 0, reasons)

    # -------------------------
    # Main: produce features list in expected order
    # -------------------------
    def _compute_feature_map(self):
        """
        Compute a dictionary of feature_name -> value for all supported features.
        Any feature not present in the map will be filled with a safe default.
        """
        fmap = {}

        # URL-level
        fmap["qty_dot_url"] = self.qty_dot_url()
        fmap["qty_hyphen_url"] = self.qty_hyphen_url()
        fmap["qty_underline_url"] = self.qty_underline_url()
        fmap["qty_slash_url"] = self.qty_slash_url()
        fmap["qty_questionmark_url"] = self.qty_questionmark_url()
        fmap["qty_equal_url"] = self.qty_equal_url()
        fmap["qty_at_url"] = self.qty_at_url()
        fmap["qty_and_url"] = self.qty_and_url()
        fmap["qty_exclamation_url"] = self.qty_exclamation_url()
        fmap["qty_space_url"] = self.qty_space_url()
        fmap["qty_tilde_url"] = self.qty_tilde_url()
        fmap["qty_comma_url"] = self.qty_comma_url()
        fmap["qty_plus_url"] = self.qty_plus_url()
        fmap["qty_asterisk_url"] = self.qty_asterisk_url()
        fmap["qty_hashtag_url"] = self.qty_hashtag_url()
        fmap["qty_dollar_url"] = self.qty_dollar_url()
        fmap["qty_percent_url"] = self.qty_percent_url()
        fmap["qty_tld_url"] = self.qty_tld_url()
        fmap["length_url"] = self.length_url()

        # Domain-level
        fmap["qty_dot_domain"] = self.qty_dot_domain()
        fmap["qty_hyphen_domain"] = self.qty_hyphen_domain()
        fmap["qty_underline_domain"] = self.qty_underline_domain()
        fmap["qty_slash_domain"] = self.qty_slash_domain()
        fmap["qty_questionmark_domain"] = self.qty_questionmark_domain()
        fmap["qty_equal_domain"] = self.qty_equal_domain()
        fmap["qty_at_domain"] = self.qty_at_domain()
        fmap["qty_and_domain"] = self.qty_and_domain()
        fmap["qty_exclamation_domain"] = self.qty_exclamation_domain()
        fmap["qty_space_domain"] = self.qty_space_domain()
        fmap["qty_tilde_domain"] = self.qty_tilde_domain()
        fmap["qty_comma_domain"] = self.qty_comma_domain()
        fmap["qty_plus_domain"] = self.qty_plus_domain()
        fmap["qty_asterisk_domain"] = self.qty_asterisk_domain()
        fmap["qty_hashtag_domain"] = self.qty_hashtag_domain()
        fmap["qty_dollar_domain"] = self.qty_dollar_domain()
        fmap["qty_percent_domain"] = self.qty_percent_domain()
        fmap["qty_vowels_domain"] = self.qty_vowels_domain()
        fmap["domain_length"] = self.domain_length()
        fmap["domain_in_ip"] = self.domain_in_ip()
        fmap["server_client_domain"] = self.server_client_domain()

        # Directory/file/params
        fmap["qty_dot_directory"] = self.qty_dot_directory()
        fmap["qty_hyphen_directory"] = self.qty_hyphen_directory()
        fmap["qty_underline_directory"] = self.qty_underline_directory()
        fmap["qty_slash_directory"] = self.qty_slash_directory()
        fmap["qty_questionmark_directory"] = self.qty_questionmark_directory()
        fmap["qty_equal_directory"] = self.qty_equal_directory()
        fmap["qty_at_directory"] = self.qty_at_directory()
        fmap["qty_and_directory"] = self.qty_and_directory()
        fmap["qty_exclamation_directory"] = self.qty_exclamation_directory()
        fmap["qty_space_directory"] = self.qty_space_directory()
        fmap["qty_tilde_directory"] = self.qty_tilde_directory()
        fmap["qty_comma_directory"] = self.qty_comma_directory()
        fmap["qty_plus_directory"] = self.qty_plus_directory()
        fmap["qty_asterisk_directory"] = self.qty_asterisk_directory()
        fmap["qty_hashtag_directory"] = self.qty_hashtag_directory()
        fmap["qty_dollar_directory"] = self.qty_dollar_directory()
        fmap["qty_percent_directory"] = self.qty_percent_directory()
        fmap["directory_length"] = self.directory_length()

        fmap["qty_dot_file"] = self.qty_dot_file()
        fmap["qty_hyphen_file"] = self.qty_hyphen_file()
        fmap["qty_underline_file"] = self.qty_underline_file()
        fmap["qty_slash_file"] = self.qty_slash_file()
        fmap["qty_questionmark_file"] = self.qty_questionmark_file()
        fmap["qty_equal_file"] = self.qty_equal_file()
        fmap["qty_at_file"] = self.qty_at_file()
        fmap["qty_and_file"] = self.qty_and_file()
        fmap["qty_exclamation_file"] = self.qty_exclamation_file()
        fmap["qty_space_file"] = self.qty_space_file()
        fmap["qty_tilde_file"] = self.qty_tilde_file()
        fmap["qty_comma_file"] = self.qty_comma_file()
        fmap["qty_plus_file"] = self.qty_plus_file()
        fmap["qty_asterisk_file"] = self.qty_asterisk_file()
        fmap["qty_hashtag_file"] = self.qty_hashtag_file()
        fmap["qty_dollar_file"] = self.qty_dollar_file()
        fmap["qty_percent_file"] = self.qty_percent_file()
        fmap["file_length"] = self.file_length()

        fmap["qty_dot_params"] = self.qty_dot_params()
        fmap["qty_hyphen_params"] = self.qty_hyphen_params()
        fmap["qty_underline_params"] = self.qty_underline_params()
        fmap["qty_slash_params"] = self.qty_slash_params()
        fmap["qty_questionmark_params"] = self.qty_questionmark_params()
        fmap["qty_equal_params"] = self.qty_equal_params()
        fmap["qty_at_params"] = self.qty_at_params()
        fmap["qty_and_params"] = self.qty_and_params()
        fmap["qty_exclamation_params"] = self.qty_exclamation_params()
        fmap["qty_space_params"] = self.qty_space_params()
        fmap["qty_tilde_params"] = self.qty_tilde_params()
        fmap["qty_comma_params"] = self.qty_comma_params()
        fmap["qty_plus_params"] = self.qty_plus_params()
        fmap["qty_asterisk_params"] = self.qty_asterisk_params()
        fmap["qty_hashtag_params"] = self.qty_hashtag_params()
        fmap["qty_dollar_params"] = self.qty_dollar_params()
        fmap["qty_percent_params"] = self.qty_percent_params()
        fmap["params_length"] = self.params_length()
        fmap["tld_present_params"] = self.tld_present_params()
        fmap["qty_params"] = self.qty_params()

        fmap["email_in_url"] = self.email_in_url()

        # Network / WHOIS / DNS / SSL placeholders
        fmap["time_response"] = self.time_response()
        fmap["domain_spf"] = self.domain_spf()
        fmap["asn_ip"] = self.asn_ip()
        fmap["time_domain_activation"] = self.time_domain_activation()
        fmap["time_domain_expiration"] = self.time_domain_expiration()
        fmap["qty_ip_resolved"] = self.qty_ip_resolved()
        fmap["qty_nameservers"] = self.qty_nameservers()
        fmap["qty_mx_servers"] = self.qty_mx_servers()
        fmap["ttl_hostname"] = self.ttl_hostname()
        fmap["tls_ssl_certificate"] = self.tls_ssl_certificate()
        fmap["qty_redirects"] = self.qty_redirects()
        fmap["url_google_index"] = self.url_google_index()
        fmap["domain_google_index"] = self.domain_google_index()
        fmap["url_shortened"] = self.url_shortened()

        # Heuristic features
        brand = self.contains_brand_token()
        fmap["heuristic_brand_flag"] = 1 if brand else 0
        # minimal typo score among brands if any else large number
        min_typo = min([self.brand_typo_score(b) for b in BRAND_LIST]) if BRAND_LIST else 999
        fmap["heuristic_typo_score_min"] = min_typo
        fmap["heuristic_brand_as_subdomain"] = 1 if self.brand_as_subdomain() else 0
        fmap["heuristic_login_words"] = 1 if self.contains_login_words() else 0
        fmap["heuristic_suspicious_tld"] = 1 if self.suspicious_tld() else 0

        return fmap

    def getFeaturesList(self):
        """
        Return features in the order defined by FEATURE_ORDER.
        If FEATURE_ORDER was detected from dataset, we follow that order
        and return a list with the same length as FEATURE_ORDER.
        For any feature name not computed above, return a safe default (-1 or 0).
        """
        fmap = self._compute_feature_map()
        features = []
        for fname in FEATURE_ORDER:
            if fname in fmap:
                features.append(fmap[fname])
            else:
                # provide defaults:
                # choose -1 for unknown/placeholder numeric features, 0 for flags
                # heuristic: if name contains 'heuristic' or 'flag' default 0; else -1
                if "heuristic" in fname or "flag" in fname or "url_shortened" in fname or fname.startswith("qty_"):
                    features.append(0)
                else:
                    features.append(-1)
        return features

# If module is run directly, quick demo (requires requests)
if __name__ == "__main__":
    test_urls = [
        "https://www.google.com/",
        "http://www.gooogle.com/secure-login",
        "///",
        "https://paypal.com.secure-login-alert.com/"
    ]
    for u in test_urls:
        try:
            fe = FeatureExtraction(u)
            feat = fe.getFeaturesList()
            print(u, "-> features len:", len(feat))
            print("heuristic:", fe.heuristic_is_phishing())
        except Exception as e:
            print(u, "-> error:", e)
