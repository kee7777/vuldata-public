def is_patch_reference(ref):
    # See if a link is a patch link
    tags = [t.lower() for t in (getattr(ref, "tags", []) or [])]
    url = (getattr(ref, "url", "") or "").lower()

    if "patch" in tags:
        return True
    
    if "exploit" in tags:
        return False
    
    keywords = [
        "github.com", "gitlab.com", "/commit/", "/pull/", "/merge",
        "/merge_requests/", ".patch", ".diff", "diff="
    ]
    return any(kw in url for kw in keywords)
