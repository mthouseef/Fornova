
## Fornova

## Overview

This project is designed for web scraping with a strong recommendation to use proxies to avoid detection. The script extracts data from multiple regions and allows for limiting the number of pages extracted.

## Features

- Proxy Support: Highly recommended to use proxies for stable and uninterrupted scraping.
- Pagination Control:
  - If `limit_page = True`, the script will extract a limited number of pages.
  - Users can specify `pages_to_extract` to control the number of pages.
- Region-Based Extraction:
  - The script supports multiple regions.
  - Default test run is limited to 20 regions.

## Configuration

Modify the following parameters in the script as needed:

```python
limit_page = True  # Set to False to scrape all available pages
pages_to_extract = 10  # Define the number of pages to scrape if limit_page is True
region_to_extract = 1  # Enable or disable proxy usage
