import os
from urllib.parse import urlparse

# Define file names for each platform
PLATFORM_FILES = {
    "github": "github_patches.txt",
    "gitlab": "gitlab_patches.txt",
    "bitbucket": "bitbucket_patches.txt",
    "sourceforge": "sourceforge_patches.txt",
    "other": "other_patches.txt"
}

def get_host_type(url):
    """Return the platform based on the URL host."""
    host = urlparse(url).netloc.lower()
    if "github.com" in host:
        return "github"
    elif "gitlab.com" in host:
        return "gitlab"
    elif "bitbucket.org" in host:
        return "bitbucket"
    elif "sourceforge.net" in host:
        return "sourceforge"
    else:
        return "other"

def dispatch_patch(url, output_folder, cve_id=None):
    """Save a patch URL to the platform-specific .txt file, including CVE ID if provided."""
    platform = get_host_type(url)
    file_name = PLATFORM_FILES.get(platform, PLATFORM_FILES["other"])
    file_path = os.path.join(output_folder, file_name)

    line = f"{cve_id} {url}" if cve_id else url

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
