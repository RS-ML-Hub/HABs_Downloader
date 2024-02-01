############################
# Code developed by Salem Ibrahim SALEM on  on 16 Oct 2023
# For inquiries, please contact: salem.ibrahim@kuas.ac.jp
###########################
import time
import requests
import pandas as pd
from   bs4 import BeautifulSoup
from   natsort import natsorted


YYYYMMDD_s = "2023/01/01" 
YYYYMMDD_e = "2023/09/30"

species_id = {
	"シャットネラ属" : "3",   # "Chattonella"
	"珪藻類合計" : "45",     # "Total diatoms"

	}

#################################################################################
###... Output file
fn_ = f"HABs__{YYYYMMDD_s.replace('/','')}_{YYYYMMDD_e.replace('/','')}.csv"


# Scrape data from the tables:
def Scrape_Data(URL_Pnt, PntID):
	max_retries = 360  # Maximum number of retries
	retry_delay = 60   # Delay between retries in seconds (1 minute)
	attempt     = 0

	while attempt < max_retries:
		try:
			response = requests.get(URL_Pnt, timeout=30)

			# Check if response is successful
			if response.status_code == 200:
				soup = BeautifulSoup(response.content, 'html.parser')
				header_table = soup.find('table')
	
				if header_table is not None:
					rows = header_table.find_all('tr')
					data_dict = {"pointId": PntID}
	
					# Process rows of the first table
					for row in rows:
						header = row.td.text.strip()
						if header:  
							value = row.find_all("td")[2].text.strip()
							data_dict[header] = value
					
					df1 = pd.DataFrame.from_dict([data_dict])
	
					# Process the second table
					akashiwo_table = soup.find('table', {'class': 'akashiwoList'})
					if akashiwo_table is not None:
						rows = akashiwo_table.find_all('tr')
						akashiwo_dict = {}
	
						for row in rows:
							header = row.th.text.strip()
							values = [val.text.strip() for val in row.find_all(["td", "th"])[1:]]
							if len(values) == 0:  
								values.append(None)
							akashiwo_dict[header] = values
	
						df2 = pd.DataFrame(akashiwo_dict)
						df2.drop(columns=["確定値／速報値", "事業・調査名"], inplace=True)
						df1_rept = pd.concat([df1] * df2.shape[0], ignore_index=True)
						df_Scrape = pd.concat([df1_rept, df2], axis=1)
	
						return df_Scrape
	
				print(f"No table found for Point ID {PntID} at {URL_Pnt}. Retrying in {retry_delay} seconds...")
				attempt += 1
				time.sleep(retry_delay)
	
			else:
				print(f"Request failed with status code {response.status_code}. Retrying in {retry_delay} seconds...")
				attempt += 1
				time.sleep(retry_delay)

		except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
			# Handle both timeout and connection errors
			print(f"Request error: {e}. Retrying in {retry_delay} seconds...")
			attempt += 1
			time.sleep(retry_delay)	
			
	print(f"Failed to retrieve data after {max_retries} attempts for Point ID {PntID}")
	return pd.DataFrame()  # Return an empty DataFrame if all retries fail

			
# Create an empty DataFrame to store all availabe station between start and end dates
main_df = pd.DataFrame()

# Step 1: Make the API Request
for SpecID in species_id.values():
	url = f"https://akashiwo.jp/public/json/jsonfileKikan.php?kaiku_id=&species_id={SpecID}&gather_ymd_s={YYYYMMDD_s}&gather_ymd_e={YYYYMMDD_e}&now=254&dispid=1&saisui_value=-1&saisui_value2=-1"
	response = requests.get(url)
	data = response.json()

	# Assuming 'data' is a list of dictionaries
	df_species = pd.DataFrame(data['markers'])

	# Append the data to the main DataFrame
	main_df = pd.concat([main_df, df_species])

# Extract unique Dates
Unique_dates = natsorted(main_df['gatherYMD'].unique(), reverse=True)

data_frames_list = []

# Global DataFrame to store all the scraped data                                                 
df_data_all = pd.DataFrame()
Pnt_Count = 1

# Extract Table data
for date_ in Unique_dates:
	df_date = main_df[main_df['gatherYMD'] == date_]

	# Extract unique Point ID
	Unique_PntID = natsorted(df_date['pointId'].unique())

	for PntID in Unique_PntID:
		df_Pnt        = df_date[df_date['pointId'] == PntID]
		Spec_Name_Pnt = df_Pnt.iloc[0]['speciesNameKana']
		Spec_id_Pnt   = species_id[Spec_Name_Pnt]
		Date_Pnt      = df_Pnt.iloc[0]['gatherYMD'].replace("-", "/")  # (2022-07-01)  > (2022/07/01)
		
		URL_Pnt = f"https://akashiwo.jp/private/akashiwoListInit.php?qpoint_id={PntID}&qspecies_id={Spec_id_Pnt}&qgather_ymd_s=&qgather_ymd_e={Date_Pnt}"
		#print(URL_Pnt)
		print(f"{Pnt_Count} Date = {date_} Point ID = {PntID}")
		df_Scrape = Scrape_Data(URL_Pnt, PntID)
		
		# Append the DataFrame to the list (instead of concatenating)
		data_frames_list.append(df_Scrape)

		# Increment the counter
		Pnt_Count += 1

		# Check if counter is a multiple of 100
		if Pnt_Count % 100 == 0:
			print(f"Saving after processing {Pnt_Count} points.")
			df_data_all = pd.concat([df_data_all] + data_frames_list, ignore_index=False)
			# remove duplication
			df_data_all.drop_duplicates(inplace=True) 						
			df_data_all.to_csv(fn_, index=True, encoding='utf-8-sig')
			
			# reset the list 
			data_frames_list = []
			
		if Pnt_Count % 50 == 0:
			time.sleep(5)
			
# After all data is collected, concatenate DataFrames in the list with existing DataFrame
df_data_all = pd.concat([df_data_all] + data_frames_list, ignore_index=False)
df_data_all.drop_duplicates(inplace=True) # remove duplication

# Save to a CSV file
df_data_all.to_csv(fn_, index=True, encoding='utf-8-sig')
