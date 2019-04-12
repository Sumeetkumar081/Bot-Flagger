
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 19:32:45 2018
 
@author: sumkumar
"""
 
 
import time
import omniture
from datetime import datetime,timedelta
import json
import uuid
import binascii
import hashlib
import requests
 
'''    
----------------------------Setting up of all variables-------------------------------------   
'''
                                 
                                 
#setting up the necessary Omniture variables
username='<USERNAME>'
secret='<SECRET>'
report_suite='<REPORT-SUITE>'
analytics = omniture.authenticate(username, secret)
suite = analytics.suites[report_suite]
 
exclude_bot_segment='<SEGMENT ID>'
bot_metric='<CALCULATED METRIC ID>'
 
ip_variable='<EVAR/PROP# FOR CAPTURING IP ADDRESS>'
ipClassVar='<CLASSIFICATION NAME FOR IP EVAR/PROP>'
 
ua_variable='<EVAR/PROP# FOR CAPTURING USER AGENT>'
uaClassVar='<CLASSIFICATION NAME FOR UA EVAR/PROP>'
 
 
email='<EMAIL>' # for classification
yesterday=(datetime.utcnow()-timedelta(hours=8)-timedelta(days=1)).strftime("%Y-%m-%d")
 
 
 
'''    
--------------------------------Running  report-----------------------------------------------   
'''
def runReport(variable):
        report = suite.report\
                .filter(segment=exclude_bot_segment)\
                .element(variable, top='20')\
                .metric(bot_metric)\
                .range(yesterday).run()
                 
        #print(report)
        val=[]
        data = report.data
        #print(data)
        for row in data:
            if (row[bot_metric]!=0 and (row[variable])!='::unspecified::' and (row[variable])!='::uniques_exceeded::'):
                val.append([row[variable],'True'])
        return val
                 
 
 
'''    
--------------------------------Defining Schema for classsification-----------------------------------------------   
'''
def omniSchema(var,classVar):
    schema={
            "check_divisions":"0",
            "description":"Bot classification",
         "element":var,
            "email_address":email,
            "export_results":"1",
            "header":[
                    "Key",
                    classVar,
                    ],
            "overwrite_conflicts":"1",
            "rsid_list":[
                 report_suite
                    ]
    }
    return schema
 
'''    
--------------------------------Classification API-----------------------------------------------   
'''
def botFlagger(rows,schema): 
      
         
        def data(x):
            i=0
            arr=[]
            jsn={}
            while i<len(x):
                jsn["row"+str(i)]=x[i]
                i+=1
            arr.append(jsn)
            return arr
            #print(arr)
         
        def _serialize_header(properties):
            #print(properties.items())
            header = []
            for key, value in properties.items():
                header.append('{key}="{value}"'.format(key=key, value=value))
                #print(header)   
            return ', '.join(header)
 
     
        def _build_token():
             nonce = str(uuid.uuid4())
             base64nonce = binascii.b2a_base64(binascii.a2b_qp(nonce))
             created_date = datetime.utcnow().isoformat() + 'Z'
             #print(created_date)
             sha = nonce + created_date + secret
             sha_object = hashlib.sha1(sha.encode())
             password_64 = binascii.b2a_base64(sha_object.digest())
             properties = {
                    "Username": username,
                    "PasswordDigest": password_64.decode().strip(),
                    "Nonce": base64nonce.decode().strip(),
                    "Created": created_date,
                }
             #print(properties)
             header = 'UsernameToken ' + _serialize_header(properties)
             return {'X-WSSE': header}  
          
         
         
         
        def runAPI(method,j):
            if method=='CreateImport':
                print("CreateImport")
                response = requests.post(
                'https://api.omniture.com/admin/1.4/rest/',
                params={'method':'Classifications.'+method},
                data=json.dumps(schema),
                headers=_build_token()
                )
                res=json.loads(response.text)
                print(res)
                jid=res['job_id']
                jid=int(jid)
                #print(jid)
                return jid
                 
            if method=='PopulateImport':           
                print("PopulateImport")
                populatePayload={}
                populatePayload['job_id']=j
                populatePayload['page']=1
                populatePayload['rows']=data(rows)
                print(populatePayload)
                 
                response = requests.post(
                'https://api.omniture.com/admin/1.4/rest/',
                params={'method':'Classifications.'+method},
                data=json.dumps(populatePayload),
                headers=_build_token()
                )
                res=json.loads(response.text)
                print(res)
             
            if method=="CommitImport":
                print("CommitImport")
                commitPayload={
                        "job_id":j
                    }
                response = requests.post(
                'https://api.omniture.com/admin/1.4/rest/',
                params={'method':'Classifications.'+method},
                data=json.dumps(commitPayload),
                headers=_build_token()
                )
                res=json.loads(response.text)
                print(res)
                 
            if method=="GetStatus":
                print("GetStatus")
                commitPayload={
                        "job_id":j
                    }
                response = requests.post(
                'https://api.omniture.com/admin/1.4/rest/',
                params={'method':'Classifications.'+method},
                data=json.dumps(commitPayload),
                headers=_build_token()
                )
                res=json.loads(response.text)
                progress=res[0]
                progress=progress['status']
                while progress!='Completed':
                    time.sleep(60)
                    response = requests.post(
                            'https://api.omniture.com/admin/1.4/rest/',
                            params={'method':'Classifications.'+method},
                            data=json.dumps(commitPayload),
                            headers=_build_token()
                            )
                    res1=json.loads(response.text)
                    progress=res1[0]
                    progress=progress['status']
                    print(res1)
                    #print('reslen',len(res))
                return int(res1[1]['id'])
                             
                             
            if method=="GetExport":
                print("GetExport")
                exportPayload={
                        "file_id":j,
                        "page":1
                        }
                response = requests.post(
                'https://api.omniture.com/admin/1.4/rest/',
                params={'method':'Classifications.'+method},
                data=json.dumps(exportPayload),
                headers=_build_token()
                )
                result=json.loads(response.text)
                time.sleep(10)
                print(result)
                               
             
        importJob=runAPI('CreateImport',1)
        print(importJob)
        runAPI('PopulateImport',importJob)
        runAPI('CommitImport',importJob)
        exportJob=runAPI('GetStatus',importJob)
        runAPI('GetExport',exportJob) 
  
 
'''    
--------------------------------Calling the functions-----------------------------------------------   
'''          
ip_list=runReport(ip_variable)
if ip_list!=[]:
    schema=omniSchema(ip_variable,ipClassVar)
    botFlagger(ip_list,schema)
 
ua_list=runReport(ua_variable)
if ua_list!=[]:
    schema=omniSchema(ua_variable,uaClassVar)
    botFlagger(ua_list,schema)
