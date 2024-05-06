# src/sierra/pipes/fuzzy.py

from fuzzywuzzy import fuzz, process
from hyfi import HyFI


def load_project_names(file_path: str, name_column: str = "project_name") -> list:
    """
    Load selected project names from a CSV file.

    Args:
        file_path (str): Path to the CSV file containing project names.
        name_column (str, optional): The column name in the CSV file that contains the project names. Defaults to "project_name".

    Returns:
        list: A list of project names.
    """
    return HyFI.load_dataframe(file_path)[name_column].str.lower().tolist()


def load_defendant_names(lawsuit_data_file: str, target_claimant: str = "sierra"):
    """
    Load extracted defendant names from lawsuit data.

    Args:
        lawsuit_data (dict): A dictionary containing lawsuit information, including defendant names.

    Returns:
        list: A list of defendant names.
    """
    lawsuit_data = HyFI.load_jsonl(lawsuit_data_file)

    return [
        defentant.lower()
        for info in lawsuit_data
        if target_claimant in ",".join(info["claimant"]).lower()
        for defentant in info["defendant"]
    ]


def fuzzy_match(project_name, defendant_names, threshold=80):
    """
    Perform fuzzy matching between a project name and a list of defendant names.

    Args:
        project_name (str): The project name to match.
        defendant_names (list): A list of defendant names to match against.
        threshold (int, optional): The minimum similarity score threshold (0-100). Defaults to 80.

    Returns:
        tuple: A tuple containing the matched defendant name and the similarity score.
               If no match is found, returns (None, None).
    """
    match = process.extractOne(
        project_name, defendant_names, scorer=fuzz.token_sort_ratio
    )
    return match if match and match[1] >= threshold else (None, None)


def match_projects_defendants(project_names, defendant_names, threshold=80):
    """
    Match project names with defendant names using fuzzy matching.

    Args:
        project_names (list): A list of project names.
        defendant_names (list): A list of defendant names.
        threshold (int, optional): The minimum similarity score threshold (0-100). Defaults to 80.

    Returns:
        list: A list of tuples containing matched project-defendant pairs and their similarity scores.
    """
    matched_pairs = []
    for project_name in project_names:
        if match := fuzzy_match(project_name, defendant_names, threshold):
            matched_pairs.append((project_name, match[0], match[1]))
        else:
            matched_pairs.append((project_name, None, None))
    return matched_pairs
