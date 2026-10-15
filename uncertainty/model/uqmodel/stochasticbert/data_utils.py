import ast
import json
import logging
import os
import pandas as pd


logger = logging.getLogger("data_utils")


def load_repo_commits(commit_file: str) -> dict:
    if commit_file.endswith(".json"):
        with open(commit_file, encoding="utf-8", mode="r") as f:
            repo_commits = json.load(f)
    else:
        with open(commit_file, encoding="utf-8", mode="r") as f:
            repo_commits = ast.literal_eval(f.read())
    return repo_commits


def check_uniq_cve(patch_commit_df: pd.DataFrame) -> bool:
    """
    Validate that each CVE maps to exactly one repo and one commit.
    Returns True if valid, False otherwise.
    """
    required = {"cve", "repo", "commit"}
    missing = required - set(patch_commit_df.columns)
    if missing:
        raise ValueError(f"check_uniq_cve: missing required columns: {sorted(missing)}")

    valid = True
    # groupby without dropping NaNs to avoid silent skips
    for cve_id, cve_df in patch_commit_df.groupby("cve", dropna=False):
        repo_nuniq = cve_df["repo"].nunique(dropna=False)
        commit_nuniq = cve_df["commit"].nunique(dropna=False)

        if repo_nuniq > 1:
            repos = ", ".join(sorted(map(str, cve_df["repo"].dropna().unique())))
            logger.info("CVE %s appears in multiple repos: %s (unexpected >1)", cve_id, repos)
            valid = False

        if commit_nuniq > 1:
            logger.info("CVE %s has multiple unique patch commits (%d, unexpected >1)", cve_id, commit_nuniq)
            valid = False
    return valid


def get_repos_patch_commits_stats(
    repo_commits: dict, patch_commit_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Build per-repo stats comparing total commits vs. patch commits.
    Avoids per-loop concat for speed; validates missing repos gracefully.
    """
    rows = []
    for repo_name, repo_df in patch_commit_df.groupby("repo", dropna=False):
        commits_all = repo_commits.get(repo_name, [])
        commits_set = set(commits_all)

        patch_commits = list(repo_df["commit"])
        patch_set = set(patch_commits)

        other_commits = commits_set - patch_set

        rows.append({
            "repo": repo_name,
            "len(commits)": len(commits_all),
            "len(set(commits))": len(commits_set),
            "len(other+patch)": len(other_commits) + len(patch_set),
            "len(patch_commits)": len(patch_commits),
            "len(set(patch_commits))": len(patch_set),
            "ratio(unique)": (len(patch_set) / len(patch_commits)) if patch_commits else 0.0,
            "len(other_commits)": len(other_commits),
        })

        if repo_name not in repo_commits:
            logger.warning("Repo %s not found in repo_commits map; treating as empty", repo_name)

    stat_df = pd.DataFrame.from_records(rows).set_index("repo")
    return stat_df


def get_data_dup_patch_commits(patch_commit_df: pd.DataFrame) -> pd.DataFrame:
    """
    Return rows where (repo, commit) duplicates exist.
    """
    required = {"repo", "commit"}
    missing = required - set(patch_commit_df.columns)
    if missing:
        raise ValueError(f"get_data_dup_patch_commits: missing required columns: {sorted(missing)}")

    dup_mask = patch_commit_df.duplicated(subset=["repo", "commit"], keep=False)
    dups = patch_commit_df.loc[dup_mask].sort_values(["repo", "commit"])

    if not dups.empty:
        dup_counts = dups.groupby(["repo", "commit"]).size().reset_index(name="count")
        for _, row in dup_counts.iterrows():
            logger.info("Duplicate patch commit: repo=%s, commit=%s, count=%s",
                        row["repo"], row["commit"], row["count"])
    return dups



def get_repo_feature_filename(data_dir: str, file_prefix: str, repo_name: str, use_shrinked: bool = True) -> str:
    """
    Build a feature CSV filename for a repo.
    (Keeps `use_shrinked` name for compatibility.)
    """
    suffix = "_shrinked.csv" if use_shrinked else ".csv"
    return os.path.join(data_dir, f"{file_prefix}_{repo_name}{suffix}")



def load_dataset_feature_data(data_dir: str, file_prefix: str, repo_list, use_shrinked: bool = True, strict: bool = True) -> pd.DataFrame:
    """
    Load per-repo feature CSVs and concatenate.
    - If strict=True, raise FileNotFoundError when a file is missing.
    - If strict=False, skip missing files with a warning.
    """
    df_list = []
    for repo_name in repo_list:
        repo_fn = get_repo_feature_filename(data_dir, file_prefix, repo_name, use_shrinked=use_shrinked)
        if not os.path.exists(repo_fn):
            msg = f"Feature file not found: {repo_fn}"
            if strict:
                raise FileNotFoundError(msg)
            logger.warning(msg + " (skipping)")
            continue
        logger.debug("loading %s ...", repo_fn)
        df_list.append(pd.read_csv(repo_fn))

    if not df_list:
        raise ValueError("No feature files were loaded—check repo_list, file_prefix, and data_dir.")
    return pd.concat(df_list, ignore_index=True)



def get_repo_list(data_dir, repo_list_fn="repo_list.csv"):
    fn = os.path.join(data_dir, repo_list_fn)
    df = pd.read_csv(fn)
    if "Repository" not in df.columns:
        raise ValueError(f"{repo_list_fn} missing required 'Repository' column.")
    return df["Repository"].astype(str).to_list()


def get_dataset_cve_list(data_dir, cve_list_fn="dataset_cve_list.csv"):
    fn = os.path.join(data_dir, cve_list_fn)
    df = pd.read_csv(fn)
    if "cve" not in df.columns:
        raise ValueError(f"{cve_list_fn} missing required 'cve' column.")
    return df["cve"].astype(str).unique()



def get_patchscout_feature_list():
    # patch scout features
    ps_columns = [
        # (VID) Vulnerability Identifier
        #     CVE-ID                                     Whether the code commit mentions the CVE-ID of the target vulnerability.
        #     Software-specific Bug-ID.	               Whether the code commit mentions the software-specific Bug-ID in the NVD
        "cve_match",
        "bug_match",
        # (VL) Vulnerability Location
        #     Same File Num 	                           # of files that appear in both code commit and NVD description.
        #     Same File Ratio                            # of same files / # of files that appear in the NVD description.
        #     Unrelated File Num                         # of files that appear in code commit but not mentioned in the NVD description.
        #     Same Function Num                          # of functions that appear in both code commit and NVD description.
        #     Same Function Ratio                        # of same functions / # of functions that appear in the NVD description.
        #     Unrelated Function Num description.        # of functions that appear in code commit but not mentioned in the NVD
        "file_same_cnt",
        "file_same_ratio",
        "file_unrelated_cnt",
        "func_same_cnt",
        "func_same_ratio",
        "func_unrelated_cnt",
        # 'filepath_same_cnt', 'filepath_same_ratio', 'filepath_unrelated_cnt',  # VCMatch
        # (VT) Vulnerability Type
        #     Vulnerability Type Relevance               The relevance of the vulnerability type-related texts between NVD information and commit message.
        #         3-tuple:
        #             Inclusion relationship
        #             Causality relationship
        #             Irrelevance relationship
        #     Patch Likelihood                           The probability of a commit to be a security patch.
        "vuln_type_1",
        "vuln_type_2",
        "vuln_type_3",  # 'patchlike', # already in data_df
        # (VDT) Vulnerability Descriptive Texts
        #     Shared-Vul-Msg-Word Num	                   # of shared words between NVD description and commit message.
        #     Shared-Vul-Msg-Word Ratio	               # of Shared-Vul-Msg-Words / # of words in NVD description.
        #     Max of Shared-Vul-Msg-Word Frequency 	   The max of the frequencies for all Shared-Vul-Msg-Words.
        #     Sum of Shared-Vul-Msg-Word Frequency 	   The sum of the frequencies for all Shared-Vul-Msg-Words.
        #     Average of Shared-Vul-Msg-Word Frequency   The average of the frequencies for all Shared-Vul-Msg-Words.
        #     Variance of Shared-Vul-Msg-Word Frequency  The variance of the frequencies for all Shared-Vul-Msg-Words.
        #     Shared-Vul-Code-Word Num	               # of shared words between NVD description and code diff.
        #     Shared-Vul-Code-Word Ratio 	               # of Shared-Vul-Code-Words / # of words in NVD description.
        #     Max of Shared-Vul-Code-Word Frequency 	   The max of the frequencies for all Shared-Vul-Code-Words.
        #     Sum of Shared-Vul-Code-Word Frequency 	   The sum of the frequencies for all Shared-Vul-Code-Words.
        #     Average of Shared-Vul-Code-Word Frequency  The average of the frequencies for all Shared-Vul-Code-Words.
        #     Variance of Shared-Vul-Code-Word Frequency The variance of the frequencies for all Shared-Vul-Code-Words.
        "mess_shared_num",
        "mess_shared_ratio",
        "mess_max",
        "mess_sum",
        "mess_mean",
        "mess_var",
        "code_shared_num",
        "code_shared_ratio",
        "code_max",
        "code_sum",
        "code_mean",
        "code_var",
    ]
    return ps_columns
