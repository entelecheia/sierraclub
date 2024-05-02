from sierra.pipes.extract_lawsuits import extract
from pathlib import Path


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


if __name__ == "__main__":
    test_extract()
