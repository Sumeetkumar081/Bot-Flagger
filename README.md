# Bot-Flagger


## How does this work?

Start by importing libraries  

1.[omniture](https://github.com/dancingcactus/python-omniture)

2.requests, hashlib ,uuid and binascii for creating token accessing Omniture API.

3.time,datetime and json usage are pretty self explainatory. 


### Declaring the global variables 
Under this section, assign the variable values into their place hoders.And,call the omniture authenticate function. 


### Reporting API
This section uses Omniture package to build the request for pulling the top 20 IP address/User agents after applying the bot calculated metric and exclude bot segment. Date range is yesterday. Lows traffic and Unspecified line items are then removed from the result.


### Classification Schema
Define the schema for [Create Import](https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/classifications-api/methods/r_CreateImport.md) classification method. 


### Classification API
Creating access token for Omniture API and then calling the classification [functions](https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/classifications-api/index.md).  The classification methods being used are CreateImport, PopulateImport,CommitImport,GetStatus and GetExport. 


### Calling the functions
This is the part where all the action happens. runReport is called to gett the bot IPs and UAs from yesterday, then omniSchema prepares the schema and finally botFlagger is called to classify those IPs and UAs as bots.
