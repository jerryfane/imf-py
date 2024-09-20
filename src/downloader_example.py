

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