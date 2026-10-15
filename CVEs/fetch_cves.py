import os
import json
import logging
import nvdlib
from patch_util import is_patch_reference
from oss_util import is_open_source_cve
from get_cvss_score import get_cvss_v3_info

def fetch_cves(start_dt, end_dt, start_str, end_str, api_key=None, checkpoint_interval=50):
    """
    Fetch CVEs from NVD within the given date range, save JSON files in a clean structure,
    and return a summary of total CVEs, patch CVEs, and OSS CVEs.
    """

    folder_name = f"{start_str}_to_{end_str}"
    patch_result_folder = os.path.join(folder_name, "patch_result")
    os.makedirs(patch_result_folder, exist_ok=True)

    logging.info(f"Fetching CVEs from {start_dt} to {end_dt}")

    args = {"pubStartDate": start_dt, "pubEndDate": end_dt}
    if api_key:
        args["key"] = api_key

    logging.info(f"Querying NVD API with args: {args}")
    results = nvdlib.searchCVE(**args)

    all_cves = []
    patch_cves = []
    oss_cves = []
    total_count = patch_total = oss_total = 0
    checkpoint_file = os.path.join(folder_name, f"checkpoint_{start_str}_to_{end_str}.json")

    for i, cve in enumerate(results):
        total_count += 1

        # Extract patch references
        patch_refs = [
            {"url": ref.url, "tags": getattr(ref, "tags", [])}
            for ref in getattr(cve, "references", []) if is_patch_reference(ref)
        ]
        if patch_refs:
            patch_total += 1

        # Check if CVE is OSS
        is_oss = is_open_source_cve(cve)
        if is_oss:
            oss_total += 1

        # Get CVSS v3 score and severity
        score, severity = get_cvss_v3_info(cve)
        if severity and isinstance(severity, str):
            severity = severity.strip()

        # Save CVE data
        cve_data = {
            "id": cve.id,
            "published": str(cve.published),
            "lastModified": str(cve.lastModified),
            "description": cve.descriptions[0].value if cve.descriptions else "",
            "is_open_source": is_oss,
            "cvss_v3_score": score,
            "cvss_v3_severity": severity,
            "patch_references": patch_refs
        }

        all_cves.append(cve_data)
        if patch_refs:
            patch_cves.append(cve_data)
        if is_oss:
            oss_cves.append(cve_data)

        # Save checkpoint periodically
        if (i+1) % checkpoint_interval == 0:
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(all_cves, f, indent=4, ensure_ascii=False)
            logging.info(f"Checkpoint saved after {i+1} CVEs")

    # Save main JSON files into folder_name
    files_to_save = {
        f"all_cves_{start_str}_to_{end_str}.json": all_cves,
        f"patch_cves_{start_str}_to_{end_str}.json": patch_cves,
        f"oss_cves_{start_str}_to_{end_str}.json": oss_cves,
    }

    for fname, data in files_to_save.items():
        fpath = os.path.join(folder_name, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info(f"Saved {len(data)} CVEs -> {fpath}")

    return {
        "total_cves": total_count,
        "cves_with_patch_links": patch_total,
        "open_source_cves": oss_total
    }
