import logging
import uuid
from typing import Dict, List

from hyfi import HyFI

from sierra.models.lawsuit import LawsuitExtractor

logger = logging.getLogger(__name__)


def assign_uuids(data: List[Dict]) -> List[Dict]:
    for item in data:
        if "uuid" not in item:
            item["uuid"] = str(uuid.uuid4())
    return data


def extract_lawsuit_details(
    data: List[Dict], extractor: LawsuitExtractor
) -> List[Dict]:
    extracted_data = []
    for item in data:
        try:
            text = item["content"]
            if "lawsuit" not in text.lower():
                logger.info(
                    "No lawsuit-related content found in item with UUID: %s",
                    item["uuid"],
                )
                continue
            logger.info(
                "Extracting lawsuit details from item with UUID: %s", item["uuid"]
            )
            lawsuit_details = extractor.extract(text)
            if not lawsuit_details.has_lawsuit:
                logger.info("No lawsuit found in item with UUID: %s", item["uuid"])
                continue
            logger.info("Lawsuit found in item with UUID: %s", item["uuid"])
            extracted_item = {
                "uuid": item["uuid"],
                "has_lawsuit": lawsuit_details.has_lawsuit,
                "claimant": lawsuit_details.claimant,
                "defendant": lawsuit_details.defendant,
                "case_summary": lawsuit_details.case_summary,
                "case_date": lawsuit_details.case_date,
                "other_details": lawsuit_details.other_details,
            }
            extracted_data.append(extracted_item)
        except Exception as e:
            logger.error("Error extracting lawsuit details for UUID: %s", item["uuid"])
            logger.error("Error: %s", e)
    return extracted_data


def extract(
    scraped_data_file: str = "scraped_data.json",
    extracted_data_file: str = "extracted_lawsuit_data.json",
):

    extractor = LawsuitExtractor()

    # Load scraped press release data
    logger.info("Loading scraped data from %s", scraped_data_file)
    scraped_data = HyFI.load_jsonl(scraped_data_file)

    # Assign UUIDs to press releases
    data_with_uuids = assign_uuids(scraped_data)
    HyFI.save_jsonl(data_with_uuids, scraped_data_file)
    logger.info(
        "Assigned UUIDs to %s press releases and saved to %s",
        len(data_with_uuids),
        scraped_data_file,
    )

    # Apply LawsuitExtractor to press releases
    extracted_data = extract_lawsuit_details(data_with_uuids, extractor)

    # Store extracted lawsuit information
    HyFI.save_jsonl(extracted_data, extracted_data_file)
    logger.info(
        "Saved %s extracted lawsuit details to %s",
        len(extracted_data),
        extracted_data_file,
    )

    logger.info("Lawsuit extraction completed.")
