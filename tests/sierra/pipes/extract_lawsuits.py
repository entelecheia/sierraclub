from sierra.pipes.extract_lawsuits import extract
from pathlib import Path
from hyfi import HyFI
import pandas as pd


def test_extract():
    raw_data_dir = "workspace/data/raw"
    process_data_dir = "workspace/data/processed"
    Path(process_data_dir).mkdir(parents=True, exist_ok=True)
    scraped_data_file = Path(raw_data_dir) / "articles.jsonl"
    extracted_data_file = Path(process_data_dir) / "extracted_lawsuit_data.jsonl"
    extract(
        scraped_data_file=scraped_data_file.absolute().as_posix(),
        extracted_data_file=extracted_data_file.absolute().as_posix(),
    )


def filter_lawsuits():
    process_data_dir = "workspace/data/processed"
    lawsuit_data_file = Path(process_data_dir) / "extracted_lawsuit_data.jsonl"
    lawsuit_data = HyFI.load_jsonl(lawsuit_data_file)
    filtered = [
        info for info in lawsuit_data if "sierra" in ",".join(info["claimant"]).lower()
    ]
    defendants = [info["defendant"] for info in filtered]
    # convert into a flat list of all defendants
    defendants = sum(defendants, [])
    # remove duplicates
    defendants = list(set(defendants))
    defendant_file = Path(process_data_dir) / "sierra_defendants.txt"
    with open(defendant_file, "w") as f:
        f.write("\n".join(defendants))

    sierra_data_file = Path(process_data_dir) / "sierra_lawsuit_data.jsonl"
    HyFI.save_jsonl(filtered, sierra_data_file)
    sierra_data_csv_file = Path(process_data_dir) / "sierra_lawsuit_data.csv"
    HyFI.save_dataframes(pd.DataFrame(filtered), sierra_data_csv_file)


if __name__ == "__main__":
    # test_extract()
    filter_lawsuits()
