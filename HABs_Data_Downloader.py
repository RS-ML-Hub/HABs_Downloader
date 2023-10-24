
############################
# Code developed by Salem Ibrahim SALEM on  on 16 Oct 2023
# Bismillah
###########################
import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from natsort import natsorted


YYYYMMDD_s = "2010/01/01" 
YYYYMMDD_e = "2023/10/01" 

species_id = {
	"シャットネラ属" : "3",  # "Chattonella"
	"珪藻類合計" : "45"  # "Total diatoms"
}

# Option to read existing files with Ancillary Data to continue upon it
Read_Exist_Data = "Yes"
Exist_data_fn   = "./Output/HABs_Chattonella_Diatom_all_AncillaryData.csv"

#################################################################################

## Output Main Directory
Output_Main = "./Output" 
# create a directory if it does not exist
if not os.path.exists(Output_Main):
	os.makedirs(Output_Main)

# Scrape data from the tables:
def Scrape_Data(URL_Pnt, PntID):
	
	response = requests.get(URL_Pnt)
	soup = BeautifulSoup(response.content, 'html.parser')

	# For the first table
	header_table = soup.find('table')
	rows = header_table.find_all('tr')

	# For the first table
	header_table = soup.find('table')
	try:
		rows = header_table.find_all('tr')
	except AttributeError:
		print("Error Table retrieval")
		return pd.DataFrame()  # Returns an empty DataFrame

	# Data storage
	data_dict = {}
	
	# Add the Point ID as it is not provided in the table
	data_dict["pointId"] = PntID
	
	# Loop through the rows
	for row in rows:
		# Extract the header
		header = row.td.text.strip()
		
		# Check if the row contains data
		if header:  
			# Extract the value (which is typically the third element)
			value = row.find_all("td")[2].text.strip()
			
			# Store in the dictionary
			data_dict[header] = value
			
	# Convert the data dictionary to a DataFrame
	df1 = pd.DataFrame.from_dict([data_dict])

	# For the akashiwoList table
	akashiwo_table = soup.find('table', {'class': 'akashiwoList'})
	try:
		rows = akashiwo_table.find_all('tr')
	except AttributeError:
		print("Error Table retrieval")
		return pd.DataFrame()  # Returns an empty DataFrame

	# Data storage
	akashiwo_dict = {}

	# Loop through the rows
	for row in rows:
		# Extract the parameter name (which will act as a header)
		header = row.th.text.strip()
		
		# Extract the data values for the current header
		values = [val.text.strip() for val in row.find_all(["td", "th"])[1:]]
		
		# If data is missing, fill with None
		if len(values) == 0:  # since we expect at least one columns
			values.append(None)
		
		akashiwo_dict[header] = values

	# Convert the data dictionary to a DataFrame
	df2 = pd.DataFrame(akashiwo_dict)
	
	# drop columns "確定値／速報値" Final value/Preliminary value and "事業・調査名" Project/survey name" from the dataframe as they have issue to scape
	df2.drop(columns=["確定値／速報値", "事業・調査名"], inplace=True)


	# Repeat the first dataframe for the number of rows in the second dataframe
	df1_rept = pd.concat([df1] * df2.shape[0], ignore_index=True)

	df_Scrape = pd.concat([df1_rept, df2], axis=1)
	return df_Scrape

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

# Save available Stations
fn_1 = os.path.join(Output_Main, f"HABs_AvailableData_Chattonella_Diatom_{YYYYMMDD_s.replace('/','')}_{YYYYMMDD_e.replace('/','')}.csv" )
main_df.to_csv(fn_1, index=True, encoding='utf-8-sig')

# Consider only stations with data
#main_df = main_df[main_df["icon"] == "●"] # We Will consider both "x" & "●" because "x" means "0"

# Extract unique Dates
Unique_dates = natsorted(main_df['gatherYMD'].unique())

# Load existing data if present
if Read_Exist_Data == "Yes":
	
	df_data_all = pd.read_csv(Exist_data_fn, index_col=0)
	Pnt_Count = df_data_all.groupby(['pointId', '採取日']).size().shape[0] # No of unique points & dates																										
else:
	# Global DataFrame to store all the scraped data
	df_data_all = pd.DataFrame()
	Pnt_Count = 1

# Extract Table data
for date_ in Unique_dates:
	df_date = main_df[main_df['gatherYMD'] == date_]

	# Extract unique Point ID
	Unique_PntID = natsorted(df_date['pointId'].unique())

	for PntID in Unique_PntID:
		df_Pnt		  = df_date[df_date['pointId'] == PntID]
		Spec_Name_Pnt = df_Pnt.iloc[0]['speciesNameKana']
		Spec_id_Pnt   = species_id[Spec_Name_Pnt]
		Date_Pnt	  = df_Pnt.iloc[0]['gatherYMD'].replace("-", "/")  # (2022-07-01)  > (2022/07/01)
		
		
		URL_Pnt = f"https://akashiwo.jp/private/akashiwoListInit.php?qpoint_id={PntID}&qspecies_id={Spec_id_Pnt}&qgather_ymd_s=&qgather_ymd_e={Date_Pnt}"
		#print(URL_Pnt)
		print(f"{Pnt_Count} Date = {date_} Point ID = {PntID}")
		df_Scrape = Scrape_Data(URL_Pnt, PntID)
		df_data_all = pd.concat([df_data_all, df_Scrape])

		# Increment the counter
		Pnt_Count += 1

		# Save the dataframe as CSV every 100 points
		if Pnt_Count % 100 == 0:
			print(f"Saving after processing {Pnt_Count} points.")
			df_data_all.drop_duplicates(inplace=True) # remove duplication
			fn_2 = os.path.join(Output_Main, "HABs_Chattonella_Diatom_all_AncillaryData.csv")
			df_data_all.to_csv(fn_2, index=True, encoding='utf-8-sig')
			
			# reset the list 
			data_frames_list = []

		if Pnt_Count % 20 == 0:
			time.sleep(5)
														  
# Save to a CSV file
fn_2 = os.path.join(Output_Main, "HABs_Chattonella_Diatom_all_AncillaryData.csv")
df_data_all.to_csv(fn_2, index=True, encoding='utf-8-sig')
