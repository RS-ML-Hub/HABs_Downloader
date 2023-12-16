# Retrieve Harmful Algal Blooms Data
- This script is designed to download in situ data related to Harmful Algal Blooms (HABs) from the Akashiwo "red tide" network, managed by the Fisheries Agency of Japan.  
- The script automates the process of finding and retrieving available HABs data of Chattonella and Total Diatom within a specified date range and collects Ancillary Data from each station.

### Dependencies
This code was developed using Windows 11 and Python 3.10. We recommend creating a new conda environment and installing the required dependencies with the following commands:
```
conda env create -f environment.yml
conda activate u-tilise
```

### Data Source
- The HABs data are sourced from the [Akashiwo network](https://akashiwo.jp/) of the Fisheries Agency, Japan.

### Targeted Species
- Chattonella
- Total Diatom

Script Workflow
Date Range Specification: The script searches for available HABs data between a user-defined start and end date.
Data Retrieval: It loops over each station to retrieve both HABs data and Ancillary Data.
Configuration Variables in HABs_Data_Downloader.py
YYYYMMDD_s: Start date in "YYYY/MM/DD" format. Example: "2020/01/01"
YYYYMMDD_e: End date in "YYYY/MM/DD" format. Example: "2023/01/01"
Usage Instructions
Set Date Range: Open HABs_Data_Downloader.py and set the YYYYMMDD_s and YYYYMMDD_e variables to your desired start and end dates.
Run the Script: Execute the script in your Python environment to begin data retrieval.


#### Variables in "HABs_Data_Downloader.py"
- YYYYMMDD_s: Start date. (e.g., "2020/01/01" )
- YYYYMMDD_e: End date.   (e.g., "2023/01/01" )
