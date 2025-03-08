import asyncio
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai import AsyncWebCrawler
import os
import subprocess
from urllib.parse import urlparse

from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

def download_markdown_files(github_url: str):
  # Parse the GitHub URL
  parsed_url = urlparse(github_url)
  path_parts = parsed_url.path.strip("/").split("/")
  
  if len(path_parts) < 4 or path_parts[1] != "blob":
    raise ValueError("Invalid GitHub file path. Use raw.githubusercontent.com URL or direct repo path.")
  
  # Extract repo details
  username, repo, _, branch, *folder_path = path_parts
  raw_base_url = f"https://raw.githubusercontent.com/{username}/{repo}/{branch}/{'/'.join(folder_path)}/"
  
  # Create output directory if it doesn't exist
  output_dir = '.docs/' + repo
  os.makedirs(output_dir, exist_ok=True)
  
  # Run wget command to download only Markdown files
  wget_command = [
    "wget", "-r", "-A", "*.md", "-np", "-nH", "--cut-dirs=3", "-R", "index.html*",
    "-P", output_dir, raw_base_url
  ]
  subprocess.run(wget_command, check=True)
  print(f"Markdown files downloaded to: {output_dir}")

# Example usage
github_path = "https://github.com/unclecode/crawl4ai/tree/main/docs/md_v2"
# download_markdown_files(github_path)

import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

async def download_docs(url: str):
  domain = urlparse(url).netloc.replace(".", "_")
  config = CrawlerRunConfig(
    deep_crawl_strategy=BestFirstCrawlingStrategy(
      max_depth=1, 
      include_external=False,
    ),
    markdown_generator=DefaultMarkdownGenerator(content_filter=PruningContentFilter()),
    scraping_strategy=LXMLWebScrapingStrategy(),
    verbose=True
  )

  async with AsyncWebCrawler() as crawler:
    results = await crawler.arun(url=url, config = config)
    print(f"Crawled {len(results)} pages in total")

  # if result success add to markdowns
  markdowns = [result.markdown.fit_markdown for result in results if result.success]
    # append all markdowns to a single file
  with open(f".docs/{domain}.md", "w") as f:
    f.write("\n\n".join(markdowns))


if __name__ == "__main__":
  asyncio.run(download_docs("https://docs.crawl4ai.com"))

# async def main():
#   # Create an instance of AsyncWebCrawler
#   async with AsyncWebCrawler() as crawler:
#     # Run the crawler on a URL
#     result = await crawler.arun(url="https://docs.crawl4ai.com/core/simple-crawling/")
#     # https://github.com/unclecode/crawl4ai/tree/main/docs/md_v2")
#
#     # Print the extracted content
#     print(result.markdown.fit_markdown)
#
# # Run the async main function
# asyncio.run(main())
