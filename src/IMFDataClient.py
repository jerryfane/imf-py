import requests
from typing import Dict, List, Any, Optional
import pandas as pd
from functools import partial
from ratelimit import limits, sleep_and_retry
from requests.exceptions import RequestException

class IMFDataClient:
    BASE_URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc"

    def __init__(self):
        self.session = requests.Session()
        self.dataflow_cache = None
        self.data_structures = {}

    @sleep_and_retry
    @limits(calls=10, period=5)
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint}"
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except RequestException as e:
                if attempt == max_retries - 1:
                    raise
                print(f"Request failed. Retrying... (Attempt {attempt + 1}/{max_retries})")

    def get_dataflow(self) -> List[Dict[str, Any]]:
        if self.dataflow_cache is None:
            response = self._make_request("Dataflow")
            self.dataflow_cache = response['Structure']['Dataflows']['Dataflow']
        return self.dataflow_cache

    def get_valid_ids(self) -> List[str]:
        dataflows = self.get_dataflow()
        return [df['KeyFamilyRef']['KeyFamilyID'] for df in dataflows]

    def validate_id(self, database_id: str) -> None:
        valid_ids = self.get_valid_ids()
        if database_id not in valid_ids:
            raise ValueError(f"DatabaseID '{database_id}' not found in Dataflow datasets. "
                             f"Valid IDs are: {', '.join(valid_ids)}")

    def get_data_structure(self, database_id: str) -> Dict[str, Any]:
        self.validate_id(database_id)
        if database_id not in self.data_structures:
            self.data_structures[database_id] = self._make_request(f"DataStructure/{database_id}")
        return self.data_structures[database_id]

    def extract_dimension_names(self, data_structure: Dict[str, Any]) -> Dict[str, str]:
        dimensions = data_structure['Structure']['KeyFamilies']['KeyFamily']['Components']['Dimension']
        return {dim['@conceptRef'].lower(): dim['@codelist'] for dim in dimensions}

    def extract_dimension_values(self, data_structure: Dict[str, Any], dimension_names: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
        code_lists = data_structure['Structure']['CodeLists']['CodeList']
        dimension_values = {}
        for dim_name, codelist_id in dimension_names.items():
            codes = next(cl['Code'] for cl in code_lists if cl['@id'] == codelist_id)
            dimension_values[dim_name] = [{'Value': code['@value'], 'Description': code['Description']['#text']} for code in codes]
        return dimension_values

    def load_dataset(self, database_id: str):
        data_structure = self.get_data_structure(database_id)
        dimension_names = self.extract_dimension_names(data_structure)
        dimension_values = self.extract_dimension_values(data_structure, dimension_names)
        
        @sleep_and_retry
        @limits(calls=10, period=5)
        def get_series(**kwargs):
            dimensions = {k: v for k, v in kwargs.items() if k in dimension_names}
            start_period = kwargs.get('start_period')
            end_period = kwargs.get('end_period')
            
            # Validate dimension values
            for dim, values in dimensions.items():
                if values is not None:
                    valid_values = [v['Value'] for v in dimension_values[dim]]
                    if isinstance(values, str):
                        values = [values]
                    if not set(values).issubset(valid_values):
                        invalid = set(values) - set(valid_values)
                        raise ValueError(f"Invalid value(s) {invalid} for dimension '{dim}'")

            # Construct the query
            if database_id == "BOP":
                # Special handling for BOP dataset
                freq = dimensions.get('freq', [''])[0]
                ref_area = '+'.join(dimensions.get('ref_area', ['']))
                indicator = '+'.join(dimensions.get('indicator', ['']))
                query = f"{freq}.{ref_area}.{indicator}"
            else:
                query_parts = []
                for dim in dimension_names.keys():
                    if dim in dimensions and dimensions[dim]:
                        values = dimensions[dim] if isinstance(dimensions[dim], list) else [dimensions[dim]]
                        query_parts.append(f"{dim}.{'+'.join(values)}")
                    else:
                        query_parts.append(dim + ".")  # Add empty placeholder for missing dimensions
                query = ".".join(query_parts)

            endpoint = f"CompactData/{database_id}/{query}"
            
            params = {}
            if start_period:
                params['startPeriod'] = start_period
            if end_period:
                params['endPeriod'] = end_period
            
            # Make the API request
            data = self._make_request(endpoint, params)

            # Process the response
            series = data['CompactData']['DataSet'].get('Series', [])
            if not isinstance(series, list):
                series = [series]

            df_list = []
            for s in series:
                obs = s.get('Obs', [])
                if not isinstance(obs, list):
                    obs = [obs]
                df = pd.DataFrame(obs)
                if not df.empty:
                    if len(df.columns) >= 2:
                        df.columns = ['TIME_PERIOD', 'OBS_VALUE'] + [f'COL_{i}' for i in range(2, len(df.columns))]
                    else:
                        print(f"Warning: Unexpected data structure for series: {s}")
                        continue
                    for dim in dimension_names:
                        if f'@{dim.upper()}' in s:
                            df[dim] = s[f'@{dim.upper()}']
                    df_list.append(df)

            if df_list:
                result = pd.concat(df_list, ignore_index=True)
                result['TIME_PERIOD'] = pd.to_datetime(result['TIME_PERIOD'])
                result['OBS_VALUE'] = pd.to_numeric(result['OBS_VALUE'], errors='coerce')
                return result
            else:
                return pd.DataFrame()  # Return empty DataFrame if no data

        return {
            'id': database_id,
            'dimensions': dimension_values,
            'get_series': get_series
        }

    def list_datasets(self) -> pd.DataFrame:
        dataflows = self.get_dataflow()
        return pd.DataFrame([
            {'ID': df['KeyFamilyRef']['KeyFamilyID'], 'Description': df['Name']['#text']}
            for df in dataflows
        ]).sort_values('ID').reset_index(drop=True)