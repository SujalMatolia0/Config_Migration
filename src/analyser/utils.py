"""
Shared utility functions used across analyser modules.
"""

def get_all_tabs_flat(tabs_list):
    """Recursively flatten nested tabsets into a single list of tab dicts."""
    flat = []
    for t in tabs_list:
        flat.append(t)
        for ts in t.get("nested_tabsets", []):
            for sub_t in ts.get("sub_tabs", []):
                flat.extend(get_all_tabs_flat([sub_t]))
    return flat

def normalise_id(val):
    """Return str(val) for consistent dict key comparisons regardless of int/str source."""
    return str(val) if val is not None else None

def is_custom_script_url(url):
    """Return True if URL points to an OSVC custom PHP script path."""
    if not url:
        return False
    u = url.lower()
    return "php/custom" in u or "gcb.cfg/php/custom" in u or ".cfg/php/custom" in u

def safe_basename(url):
    """
    Return the filename portion of a URL path.
    Falls back to the full URL if path is empty or ends with /.
    """
    import urllib.parse
    try:
        path = urllib.parse.urlparse(url).path.rstrip("/")
        base = path.split("/")[-1] if path else ""
        return base if base else url
    except Exception:
        return url
