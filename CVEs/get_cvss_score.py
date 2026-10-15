def get_cvss_v3_info(cve):
    """
    Returns the CVSS v3 score and severity for a given CVE object.
    Tries v3.1 first, falls back to v3.0.
    """
    score, severity = None, None
    if hasattr(cve, "metrics") and cve.metrics:
        m = cve.metrics
        # Try v3.1 first
        if hasattr(m, "cvssMetricV31") and m.cvssMetricV31:
            cvss = m.cvssMetricV31[0].cvssData
            score = getattr(cvss, "baseScore", None)
            severity = getattr(cvss, "baseSeverity", None)
        # Fallback to v3.0 if v3.1 missing
        elif hasattr(m, "cvssMetricV30") and m.cvssMetricV30:
            cvss = m.cvssMetricV30[0].cvssData
            score = getattr(cvss, "baseScore", None)
            severity = getattr(cvss, "baseSeverity", None)
    return score, severity
