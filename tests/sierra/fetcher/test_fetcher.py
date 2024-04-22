from sierra.fetcher import SierraClubFetcher


def test_generate_config():
    SierraClubFetcher.generate_config()


def test_sierra_fetcher():
    siera = SierraClubFetcher(
        search_keywords=[],
        max_num_pages=1,
        max_num_articles=1,
        verbose=True,
        output_dir="workspace/test/sierraclub",
        overwrite_existing=True,
    )
    assert (
        siera.search_url
        == "https://www.sierraclub.org/press-releases?_wrapper_format=html&page={page}"
    )
    siera.fetch_links()
    siera.fetch_articles()


if __name__ == "__main__":
    test_generate_config()
    test_sierra_fetcher()
