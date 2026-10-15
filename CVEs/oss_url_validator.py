import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from url_checker import check_url_alive
from patch_adapter import get_host_type

def validate_and_dispatch_oss(patch_cves_file, patch_result_folder, max_workers=50):
    if not os.path.exists(patch_cves_file):
        logging.error(f"File not found: {patch_cves_file}")
        return

    with open(patch_cves_file, "r", encoding="utf-8") as f:
        patch_cves = json.load(f)

    alive_cves = []
    dead_cves = []
    alive_urls = []
    dead_urls = []

    # Track URL counts per platform
    alive_platform_url_count = {}
    dead_platform_url_count = {}
    # Track full CVE info per platform
    platform_patch_cves = {}

    logging.info(f"Starting patch URL validation and platform dispatch...")
    logging.info(f"Checking {len(patch_cves)} CVEs...")

    def check_and_dispatch(cve):
        patch_refs = cve.get("patch_references", [])
        if not patch_refs:
            return False

        any_alive = False
        for ref in patch_refs:
            url = ref["url"]
            alive = check_url_alive(url)
            platform = get_host_type(url)

            # Create folder for this platform
            platform_folder = os.path.join(patch_result_folder, platform)
            os.makedirs(platform_folder, exist_ok=True)

            # Track alive/dead URLs
            if alive:
                any_alive = True
                alive_urls.append({"cve_id": cve.get("id"), "url": url})
                alive_platform_url_count[platform] = alive_platform_url_count.get(platform, 0) + 1
            else:
                dead_urls.append({"cve_id": cve.get("id"), "url": url})
                dead_platform_url_count[platform] = dead_platform_url_count.get(platform, 0) + 1

            # Track full CVE info per platform
            platform_patch_cves.setdefault(platform, []).append(cve)

            # Save alive/dead URLs per platform
            with open(os.path.join(platform_folder, "alive_urls.json"), "w", encoding="utf-8") as f:
                json.dump([u for u in alive_urls if get_host_type(u["url"]) == platform], f, indent=4)
            with open(os.path.join(platform_folder, "dead_urls.json"), "w", encoding="utf-8") as f:
                json.dump([u for u in dead_urls if get_host_type(u["url"]) == platform], f, indent=4)

        return any_alive

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_cve = {executor.submit(check_and_dispatch, cve): cve for cve in patch_cves}
        for i, future in enumerate(as_completed(future_to_cve), 1):
            cve = future_to_cve[future]
            try:
                if future.result():
                    alive_cves.append(cve)
                else:
                    dead_cves.append(cve)
            except Exception as e:
                logging.error(f"Error processing {cve.get('id')}: {e}")
                dead_cves.append(cve)

            if i % 10 == 0 or i == len(patch_cves):
                logging.info(f"Checked {i}/{len(patch_cves)} CVEs")

    # Save overall CVE JSONs
    with open(os.path.join(patch_result_folder, "alive_cves.json"), "w", encoding="utf-8") as f:
        json.dump(alive_cves, f, indent=4, ensure_ascii=False)
    with open(os.path.join(patch_result_folder, "dead_cves.json"), "w", encoding="utf-8") as f:
        json.dump(dead_cves, f, indent=4, ensure_ascii=False)

    # Save overall URL JSONs
    with open(os.path.join(patch_result_folder, "alive_urls.json"), "w", encoding="utf-8") as f:
        json.dump(alive_urls, f, indent=4, ensure_ascii=False)
    with open(os.path.join(patch_result_folder, "dead_urls.json"), "w", encoding="utf-8") as f:
        json.dump(dead_urls, f, indent=4, ensure_ascii=False)

    # Save full CVE data per platform as JSON
    for platform, cves in platform_patch_cves.items():
        platform_folder = os.path.join(patch_result_folder, platform)
        file_path = os.path.join(platform_folder, f"{platform}_patches_cves.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cves, f, indent=4, ensure_ascii=False)

    # Final summary logging
    logging.info(f"Alive CVEs: {len(alive_cves)}")
    logging.info(f"Dead CVEs: {len(dead_cves)}")
    logging.info(f"Alive URLs: {len(alive_urls)}")
    logging.info(f"Dead URLs: {len(dead_urls)}")

    all_platforms = set(alive_platform_url_count.keys()) | set(dead_platform_url_count.keys())
    for platform in sorted(all_platforms):
        alive_count = alive_platform_url_count.get(platform, 0)
        dead_count = dead_platform_url_count.get(platform, 0)
        logging.info(f"{platform.capitalize()}: Alive: {alive_count} Dead: {dead_count}")

    logging.info("Patch URL validation and platform dispatch completed.")
