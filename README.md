# IMF Data Client and Downloader

This project provides a Python client for interacting with the [IMF Data Services API](https://datahelp.imf.org/knowledgebase/articles/667681-json-restful-web-service), along with a data downloader script for efficiently retrieving large datasets.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
   - [Basic Usage](#basic-usage)
   - [Advanced Usage (Data Downloader)](#advanced-usage-data-downloader)
4. [How It Works](#how-it-works)
5. [File Descriptions](#file-descriptions)
6. [API Rate Limits](#api-rate-limits)
7. [Troubleshooting](#troubleshooting)

## Overview

The IMF Data Client and Downloader consists of three main components:

1. `IMFDataClient`: A Python class for interacting with the IMF Data Services API.
2. `downloader_example.py`: A simple script demonstrating basic usage of the IMFDataClient.
3. `downloader_chunks_example.py`: An advanced script for downloading large datasets in chunks.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/imf-data-client.git
   cd imf-data-client
   ```

2. Install the required dependencies:
   ```
   pip install requests pandas tqdm ratelimit
   ```

## Usage

### Basic Usage

For basic usage, you can use the `IMFDataClient` class directly:

```python
from IMFDataClient import IMFDataClient

client = IMFDataClient()
bop_dataset = client.load_dataset("BOP")

data = bop_dataset['get_series'](
    freq = ["Q"],  # Quarterly frequency
    ref_area = ["ES", "PT", "AF", "AL"], 
    indicator = ["BXGS_BP6_USD"],
    start_period = "2005"
)

print(data)
```

This will retrieve quarterly data for the specified countries and indicator from 2005 onwards.

### Advanced Usage (Data Downloader)

For downloading large datasets, use the `downloader_chunks_example.py` script:

1. Modify the `indicators` list in the script to include the indicators you want to download.
2. Adjust the chunk sizes for indicators and countries if needed:
   ```python
   indicator_chunks = chunk_list(indicators, 2)
   country_chunks = chunk_list(all_ref_areas, 6)
   ```
3. Run the script:
   ```
   python downloader_chunks_example.py
   ```

The script will download data in chunks and periodically save it to a CSV file.

## How It Works

1. The `IMFDataClient` class:
   - Handles authentication and communication with the IMF Data Services API.
   - Caches dataset structures to minimize API calls.
   - Implements rate limiting to comply with API usage restrictions.

2. The data downloader script:
   - Chunks the list of indicators and countries to make smaller, manageable API requests.
   - Downloads data for each chunk and combines the results.
   - Periodically saves the downloaded data to a CSV file to prevent data loss in case of interruptions.
   - Uses a progress bar to show download progress.

## File Descriptions

- `IMFDataClient.py`: Contains the `IMFDataClient` class for interacting with the IMF API.
- `downloader_example.py`: A simple example script for basic usage of the IMFDataClient.
- `downloader_chunks_example.py`: An advanced script for downloading large datasets in chunks.

## API Rate Limits

The IMF Data Services API has the following rate limits:

- 10 requests in a 5-second window from one user (IP)
- 50 requests per second overall on the application

The `IMFDataClient` class implements rate limiting to comply with these restrictions.

## Troubleshooting

- If you encounter "Bad Request" errors, try reducing the chunk sizes in the downloader script.
- For other API-related errors, check the error message for details and ensure you're using valid country codes and indicator codes.

For more information about the IMF Data Services API, refer to the official [IMF documentation](https://datahelp.imf.org/knowledgebase/articles/667681-json-restful-web-service).
