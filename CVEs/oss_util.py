OSS_HOSTS = {
    "github.com","gitlab.com","bitbucket.org","sourceforge.net",
    "apache.org","kernel.org","mozilla.org","debian.org","ubuntu.com",
    "gnome.org","kde.org"
}
OSS_VENDOR_HINTS = {
    "apache","linux","mozilla","debian","canonical","redhat","gnome","kde",
    "curl","openssl","postgresql","sqlite","nginx","grafana","kubernetes","prometheus"
}

def is_open_source_cve(cve):
    # Check if CVE is from open source
    for ref in (getattr(cve, "references", []) or []):
        url = (getattr(ref, "url", "") or "").lower()
        if any(h in url for h in OSS_HOSTS):
            return True
    cfgs = getattr(cve, "configurations", None)
    if cfgs and getattr(cfgs, "nodes", None):
        for node in cfgs.nodes:
            for match in (getattr(node, "cpeMatch", []) or []):
                cpe = getattr(match, "criteria", "") or getattr(match, "cpe23Uri","")
                parts = cpe.split(":")
                if len(parts) >= 5 and parts[2] == "a":
                    vendor = parts[3].lower()
                    if any(vendor.startswith(h) for h in OSS_VENDOR_HINTS):
                        return True
    return False
