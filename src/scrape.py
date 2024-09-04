import asyncio
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee.errors import SessionError
from argparse import ArgumentParser
from typing import Dict, List
from markdownify import markdownify as md


async def scrape_urls(urls: List[str], keywords: List[str]) -> Dict[str, str]:
    crawler = PlaywrightCrawler(
        max_requests_per_crawl=5,  # Limit the crawl to 5 requests.
        headless=True,  # Run in headless mode.
        browser_type='chromium',  # Use the Chromium browser.
        # max_retries=3,  # Set maximum retries for failed requests.
    )

    # Store extracted data
    extracted_data = []

    # Define the default request handler, which will be called for every request.
    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        context.log.info(f'Processing {context.request.url} ...')

        # Initialize a list to store PDF links
        pdf_links = []

        try:
            # Get all anchor elements
            anchors = await context.page.query_selector_all("a")

            # Check each anchor for keywords in its text
            for anchor in anchors:
                link_text = await anchor.inner_text()
                link_url = await anchor.get_attribute("href")

                if any(keyword.lower() in link_text.lower() for keyword in keywords):
                    # Enqueue the link if it contains keywords in its text
                    await context.enqueue_links(
                        selector="fa[href='{link_url}']"
                    )

            # Check for PDF links and store them
            for anchor in anchors:
                link_url = await anchor.get_attribute("href")
                if link_url and link_url.lower().endswith(".pdf"):
                    pdf_links.append(link_url)

            # Log that the page contains the keyword
            if pdf_links:
                context.log.info(
                    f'Found PDF links in {context.request.url}: {pdf_links}')

            # Extract data for the current page
            data = {
                'url': context.request.url,
                'title': await context.page.title(),
                'content': md((await context.page.content()), strip=["a"]),
                'pdf_links': pdf_links,  # Add the PDF links to the data
                "error": [],
                "log": context.log
            }
            extracted_data.append(data)

        except Exception as e:
            context.log.error(f'Error processing {context.request.url}: {e}')
            data = {
                "url": context.request.url,
                "error": [f'Error processing {context.request.url}: {e}']
            }
            extracted_data.append(data)

    # Run the crawler with the initial list of URLs.
    await crawler.run(urls)

    # Log and return the extracted data
    crawler.log.info(f'Extracted data: {extracted_data}')
    return {'extracted_data': extracted_data}


async def find_target_urls(urls: List[str], keywords: List[str]) -> Dict[str, str]:
    """find embeded urls whose keywords contain certain keywords and return 
    these urls as well as their contents"""
    crawler = PlaywrightCrawler(
        max_requests_per_crawl=5,  # Limit the crawl to 5 requests.
        headless=True,  # Run in headless mode.
        browser_type='chromium',  # Use the Chromium browser.
        # max_retries=3,  # Set maximum retries for failed requests.
    )

    # Store extracted data
    extracted_data = []

    # Define the default request handler, which will be called for every request.
    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        context.log.info(f'Processing {context.request.url} ...')

        # Initialize a list to store PDF links
        url_links = []

        try:
            # Get all anchor elements
            anchors = await context.page.query_selector_all("a")

            # Check each anchor for keywords in its text
            for anchor in anchors:
                link_text = await anchor.inner_text()
                link_url = await anchor.get_attribute("href")

                if any(keyword.lower() in link_text.lower() for keyword in keywords):
                    # Enqueue the link if it contains keywords in its text
                    await context.enqueue_links(
                        selector="fa[href='{link_url}']"
                    )
                    url_links.append(link_url)
            # Extract data for the current page
            data = {
                'url': context.request.url,
                'title': await context.page.title(),
                'content': md((await context.page.content()), strip=["a"]),
                'url_links': url_links,  # Add the PDF links to the data
                "error": [],
                "log": context.log
            }
            extracted_data.append(data)

        except Exception as e:
            context.log.error(f'Error processing {context.request.url}: {e}')
            data = {
                "url": context.request.url,
                "error": [f'Error processing {context.request.url}: {e}']
            }
            extracted_data.append(data)

    # Run the crawler with the initial list of URLs.
    await crawler.run(urls)

    # Log and return the extracted data
    crawler.log.info(f'Extracted data: {extracted_data}')
    return {'extracted_data': extracted_data}


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument("-U", "--urls", nargs="+",
                           help="urls to process", required=True)
    argparser.add_argument("-K", "--keywords", nargs="+",
                           help="keywords to search for", default=["esg", "investor"], required=True)
    args = argparser.parse_args()
    asyncio.run(scrape_urls(args.urls, args.keywords))
