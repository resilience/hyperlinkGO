# hyperlinkGO

### This is a Producer/Consumer extractor that extracts hyperlinks from a .csv file

## test.py
##### this tests the following functionality of the init.py extractor: 
##### cleaning
##### markup handling
##### hyperlink extraction


## init.py
##### this is the main application
##### thread count can be specified as producer and consumer blocks run concurrently.
##### the code has rudimentary url cleaning incorporated to prevent encoding/decoding errors.
##### the input format is .csv utf-8 


Notes: 
1. a temporary storage file is created called DB-URL-list-1 STORAGE.csv 
2. the anat.co.za.html file is used as a screenshot of html to ensure if the site changes it doesn't affect the test
3. The extractor folder contains text URLS in various sizes, from 1 to 3000+
