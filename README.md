# Retrieve Harmful Algal Blooms Data

- The Harmful Algal Blooms (HABs) in situ data are downloaded from the red tide net of the Fisheries Agency, Japan (https://akashiwo.jp/)
- We consider two species: Chattonella and Total Diatom
- The script finds all available HABs data between the start and end dates.
- Then, loop over each station to retrieve Ancillary Data


#### Variables in "HABs_Data_Downloader.py"
- YYYYMMDD_s: Start date
- YYYYMMDD_e: End date.
- Read_Exist_Data: use "Yes" if you have existing data and want the new data to be append after the existing data.
