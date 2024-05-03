from pathlib import Path
from sierra.pipes.fuzzy import (
    load_project_names,
    load_defendant_names,
    match_projects_defendants,
)


def fuzzy_match():
    raw_data_dir = "workspace/data/raw"
    process_data_dir = "workspace/data/processed"

    project_names_file = Path(raw_data_dir) / "target_projects.csv"

    # Load project names from a CSV file
    project_names = load_project_names(project_names_file, "Borrower")
    print(f"Loaded {len(project_names)} project names.")

    # Load defendant names from lawsuit data
    lawsuit_data_file = Path(process_data_dir) / "extracted_lawsuit_data.jsonl"
    defendant_names = load_defendant_names(lawsuit_data_file)
    print(f"Loaded {len(defendant_names)} defendant names.")

    # # Perform fuzzy matching
    matched_pairs = match_projects_defendants(project_names, defendant_names, 80)

    # Print the matched pairs
    for project_name, defendant_name, similarity_score in matched_pairs:
        if defendant_name:
            print(
                f"Project: {project_name}, Defendant: {defendant_name}, Similarity Score: {similarity_score}"
            )


if __name__ == "__main__":
    fuzzy_match()
