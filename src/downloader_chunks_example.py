import pandas as pd
from tqdm import tqdm
import warnings
import os

# Suppress warnings
warnings.filterwarnings('ignore')

# List of all indicators
indicators = [
    "BXGS_BP6_USD", "BMGS_BP6_USD", "BXGM_BP6_USD", "BMGM_BP6_USD", "BGMZ_BP6_USD", 
    "BXGN_BP6_USD", "BMGN_BP6_USD", "BXXGT_BP6_USD", "BXMGT_BP6_USD", "BXG_BP6_USD", 
    "BMG_BP6_USD", "BXGT_BP6_USD", "BXSORL_BP6_USD", "BMSORL_BP6_USD", "BXSOCNA_BP6_USD", 
    "BMSOCNA_BP6_USD", "BXSOCNAR_BP6_USD", "BMSOCNAR_BP6_USD", "BXSOCN_BP6_USD", 
    "BMSOCN_BP6_USD", "BXS_BP6_USD", "BMS_BP6_USD", "BXSOFI_BP6_USD", "BMSOFI_BP6_USD", 
    "BXSOFIEX_BP6_USD", "BMSOFIEX_BP6_USD", "BXSOFIFISM_BP6_USD", "BMSOFIFISM_BP6_USD", 
    "BXSOGGS_BP6_USD", "BMSOGGS_BP6_USD", "BXSOGGSTS_BP6_USD", "BMSOGGSTS_BP6_USD", 
    "BXSOINAI_BP6_USD", "BMSOINAI_BP6_USD", "BXSOIN_BP6_USD", "BMSOIN_BP6_USD", 
    "BXSOIND_BP6_USD", "BMSOIND_BP6_USD", "BXSOINPG_BP6_USD", "BMSOINPG_BP6_USD", 
    "BXSOINRI_BP6_USD", "BMSOINRI_BP6_USD", "BXSR_BP6_USD", "BMSR_BP6_USD", 
    "BXSM_BP6_USD", "BMSM_BP6_USD", "BXSMA_BP6_USD", "BMSMA_BP6_USD", "BXSMR_BP6_USD", 
    "BMSMR_BP6_USD", "BXSOOB_BP6_USD", "BMSOOB_BP6_USD", "BXSOOBPM_BP6_USD", 
    "BMSOOBPM_BP6_USD", "BXSOOBRD_BP6_USD", "BMSOOBRD_BP6_USD", "BXSOOBTT_BP6_USD", 
    "BMSOOBTT_BP6_USD", "BXSO_BP6_USD", "BMSO_BP6_USD", "BXSOPCRAU_BP6_USD", 
    "BMSOPCRAU_BP6_USD", "BXSOPCR_BP6_USD", "BMSOPCR_BP6_USD", "BXSOPCRO_BP6_USD", 
    "BMSOPCRO_BP6_USD", "BXSOTCMC_BP6_USD", "BMSOTCMC_BP6_USD", "BXSOTCM_BP6_USD", 
    "BMSOTCM_BP6_USD", "BXSOTCMM_BP6_USD", "BMSOTCMM_BP6_USD", "BXSOTCMT_BP6_USD", 
    "BMSOTCMT_BP6_USD", "BXSTRA_BP6_USD", "BMSTRA_BP6_USD", "BXSTRAFR_BP6_USD", 
    "BMSTRAFR_BP6_USD", "BXSTRAO_BP6_USD", "BMSTRAO_BP6_USD", "BXSTRAPA_BP6_USD", 
    "BMSTRAPA_BP6_USD", "BXSTRAPAS_BP6_USD", "BMSTRAPAS_BP6_USD", "BXSTR_BP6_USD", 
    "BMSTR_BP6_USD", "BXSTRFR_BP6_USD", "BMSTRFR_BP6_USD", "BXSTROT_BP6_USD", 
    "BMSTROT_BP6_USD", "BXSTROTFR_BP6_USD", "BMSTROTFR_BP6_USD", "BXSTROTO_BP6_USD", 
    "BMSTROTO_BP6_USD", "BXSTROTPA_BP6_USD", "BMSTROTPA_BP6_USD", "BXSTROTPAS_BP6_USD", 
    "BMSTROTPAS_BP6_USD", "BXSTRO_BP6_USD", "BMSTRO_BP6_USD", "BXSTRPA_BP6_USD", 
    "BMSTRPA_BP6_USD", "BMSTRPAS_BP6_USD", "BXSTRPAS_BP6_USD", "BXSTRPC_BP6_USD", 
    "BMSTRPC_BP6_USD", "BXSTRS_BP6_USD", "BMSTRS_BP6_USD", "BXSTRSFR_BP6_USD", 
    "BMSTRSFR_BP6_USD", "BXSTRSO_BP6_USD", "BMSTRSO_BP6_USD", "BXSTRSPA_BP6_USD", 
    "BMSTRSPA_BP6_USD", "BXSTRSPAS_BP6_USD", "BMSTRSPAS_BP6_USD", "BXSTVBS_BP6_USD", 
    "BMSTVBS_BP6_USD", "BXSTVB_BP6_USD", "BMSTVB_BP6_USD", "BXSTVBO_BP6_USD", 
    "BMSTVBO_BP6_USD", "BXSTV_BP6_USD", "BMSTV_BP6_USD", "BXSTVBPAS_BP6_USD", 
    "BMSTVBPAS_BP6_USD", "BXSTVBPFS_BP6_USD", "BMSTVBPFS_BP6_USD", "BXSTVBPG_BP6_USD", 
    "BMSTVBPG_BP6_USD", "BXSTVBPLS_BP6_USD", "BMSTVBPLS_BP6_USD", "BXSTVBPOS_BP6_USD", 
    "BMSTVBPOS_BP6_USD", "BXSTVBPOSED_BP6_USD", "BMSTVBPOSED_BP6_USD", "BXSTVBPOSH_BP6_USD", 
    "BMSTVBPOSH_BP6_USD", "BXSTVP_BP6_USD", "BMSTVP_BP6_USD", "BXSTVPH_BP6_USD", 
    "BMSTVPH_BP6_USD", "BXSTVPO_BP6_USD", "BMSTVPO_BP6_USD", "BXSTVPED_BP6_USD", 
    "BMSTVPED_BP6_USD", "BXSTROPC_BP6_USD", "BMSTROPC_BP6_USD"
]

# Function to chunk a list
def chunk_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

# Function to download data for a chunk of indicators and countries
def download_chunk_data(indicator_chunk, country_chunk):
    try:
        data = bop_dataset['get_series'](
            freq=["Q"],
            ref_area=country_chunk,
            indicator=indicator_chunk,
            start_period="2005"
        )
        return data
    except Exception as e:
        print(f"Error downloading data for indicators {indicator_chunk} and countries {country_chunk}: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

# Function to save data to CSV
def save_to_csv(data, filename, mode='w'):
    if mode == 'w' or not os.path.exists(filename):
        data.to_csv(filename, index=False, mode='w')
    else:
        data.to_csv(filename, index=False, mode='a', header=False)

# Get all reference areas
all_ref_areas = [area['Value'] for area in bop_dataset['dimensions']['ref_area']]

# Chunk the indicators and countries
indicator_chunks = chunk_list(indicators, 2)
country_chunks = chunk_list(all_ref_areas, 6)

# Download data for all chunks
all_data = []
total_chunks = len(indicator_chunks) * len(country_chunks)
output_file = "./data/imf_bop_data.csv"
save_frequency = 50  # Save every 50 chunks

with tqdm(total=total_chunks, desc="Downloading data chunks") as pbar:
    for i, indicator_chunk in enumerate(indicator_chunks):
        for j, country_chunk in enumerate(country_chunks):
            chunk_data = download_chunk_data(indicator_chunk, country_chunk)
            if not chunk_data.empty:
                all_data.append(chunk_data)
            
            # Periodic saving
            chunk_number = i * len(country_chunks) + j + 1
            if chunk_number % save_frequency == 0:
                combined_data = pd.concat(all_data, ignore_index=True)
                save_to_csv(combined_data, output_file, mode='a' if chunk_number > save_frequency else 'w')
                print(f"Saved data after {chunk_number} chunks")
                all_data = []  # Clear the list to free up memory
            
            pbar.update(1)

# Final save for any remaining data
if all_data:
    combined_data = pd.concat(all_data, ignore_index=True)
    save_to_csv(combined_data, output_file, mode='a')

print(f"All data saved to {output_file}")

# Print some statistics about the downloaded data
final_data = pd.read_csv(output_file)
print(f"Total rows of data: {len(final_data)}")
print(f"Unique countries: {final_data['ref_area'].nunique()}")
print(f"Unique indicators: {final_data['indicator'].nunique()}")
print(f"Date range: from {final_data['TIME_PERIOD'].min()} to {final_data['TIME_PERIOD'].max()}")