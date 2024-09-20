# IMF Data Client and Downloader

This project provides a Python client for interacting with the [IMF Data Services API](https://datahelp.imf.org/knowledgebase/articles/667681-json-restful-web-service), along with a data downloader script for efficiently retrieving large datasets.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
   - [Basic Usage](#basic-usage)
   - [Advanced Usage (Data Downloader)](#advanced-usage-data-downloader)
4. [How It Works](#how-it-works)
5. [IMFDataClient Class Methods](#imfdataclient-class-methods)
6. [File Descriptions](#file-descriptions)
7. [API Rate Limits](#api-rate-limits)
8. [Troubleshooting](#troubleshooting)

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

## IMFDataClient Class Methods

The `IMFDataClient` class provides several methods for interacting with the IMF Data Services API:

- `__init__()`: Initializes the client, setting up a session and caches for dataflows and data structures.

- `_make_request(endpoint, params)`: Makes a rate-limited API request to the specified endpoint with optional parameters. It includes retry logic for failed requests.

- `get_dataflow()`: Retrieves and caches the list of available dataflows (datasets) from the API.

- `get_valid_ids()`: Returns a list of valid dataset IDs based on the cached dataflow information.

- `validate_id(database_id)`: Checks if a given database ID is valid, raising a ValueError if it's not.

- `get_data_structure(database_id)`: Retrieves and caches the data structure for a specific dataset.

- `extract_dimension_names(data_structure)`: Extracts the dimension names from a dataset's structure.

- `extract_dimension_values(data_structure, dimension_names)`: Extracts the possible values for each dimension in a dataset.

- `load_dataset(database_id)`: Loads a dataset, returning a dictionary with the dataset's ID, dimensions, and a `get_series` function for data retrieval.

- `list_datasets()`: Returns a pandas DataFrame listing all available datasets with their IDs and descriptions.

The `get_series` function returned by `load_dataset` is the primary method for retrieving data. It accepts parameters for frequency, reference area, indicators, and time periods, constructs the appropriate query, makes the API request, and returns the data as a pandas DataFrame.

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
