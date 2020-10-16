# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 09:36:36 2020

@author: Bagpyp

https://developer.sidelineswap.com/doc/index.html
"""

import json
from numpy import nan
import pandas as pd
pd.options.mode.chained_assignment=None
pd.options.display.max_rows = 150
pd.options.display.max_columns = 40
pd.options.display.width = 180
pd.options.display.max_colwidth = 40
from pprint import pprint
import requests

base = 'https://developer.sidelineswap.com/v1/'
headers = {'x-api-key':'514c5cd41b5e929de0fb6b351107e9af',
           'x-client-id':'57e0ccb5-a210-463e-a38a-c9723c2e28c1',
           'accept':'application/json'}

def getCat(id=''):
    res = requests.get(base+f'categories/{id}',headers=headers)
    return res

def postList(data):
    h=headers.copy()
    h.update({'content-type':'application/json'})
    res = requests.post(base+'listings',headers=h,json=data)
    return res

def setAddress(data):
    h=headers.copy()
    h.update({'content-type':'application/json'})
    res = requests.post(base+'addresses',headers=h,json=data)
    return res

res = setAddress({'street_1': '2424 SE Burnside Rd',
 'city': 'Gresham',
 'state': 'OR',
 'zip': '97080',
 'country': 'US'})

catIDs = pd.json_normalize(json.loads(getCat().content))
details = pd.read_csv('category_detail_map.csv')
catMap = pd.read_csv('category_map.csv')
catFields = pd.read_csv('category_fields.csv')
        
catMap = catMap[catMap.uuid.notna()]
catMap.DCSname = catMap.DCSname.str.replace("'",'').str.lower()
catMap.CAT = catMap.CAT.str.replace("',",'')
catMap.uuid = catMap.uuid.str.replace('\\t','')
catMap.drop('CAT',axis=1,inplace=True)

details.DCSname = details.DCSname.str.lower()
details = details[details.DCSname.isin(catMap.DCSname)]
details['fieldDetail'] = details.detail + '::' + details.field

catFields = catFields[catFields.categoryname.isin(catMap.CATss)]
catFields['fields'] = catFields['name'] + '::' \
    + catFields.required.fillna(0).astype(str)

cdf = catMap.set_index('DCSname').join(\
details.groupby('DCSname').fieldDetail.unique()).reset_index()
cdf.fieldDetail = cdf.fieldDetail.fillna('[]')
    
#%%

df = pd.read_pickle(r'\\Server\c\Users\Administrator\RPBC2\ready.pkl')\
    .reset_index()\
    .replace({nan:None})\
    .drop(['fCreated','lModified','p_date_created','p_date_modified'], axis = 1)
df.DCSname = df.DCSname.str.replace('Hike/Pack','Hike, Pack')
df.to_pickle('currentDf.pkl')

df = df[df.DCSname.str.lower().isin(cdf.DCSname)]
# df = df[df.CAT.str.contains('Ski')]
gb = df.groupby('webName')

#%%


cat = 'Snowboard/Bindings/Women'

def useDCS(fSplit,frame):
    x = {'D':0,'C':1,'S':2}
    if fSplit[1].upper() in list('DCS'):
        return (cat.split('/')[x[fSplit[1]]]).title()
    else:
        return fSplit[1]
        
        

def categoryInfo(cat):
    cat = cat.lower()
    frame = cdf.loc[cdf.DCSname==cat,['CATss','fieldDetail']]
    data = {}
    if (frame.fieldDetail.astype(str) == '[]').values[0]:
        return frame.CATss.values[0],data
    else:
        for f in frame.fieldDetail.values[0]:
            fSplit = f.split('::')
            data.update({fSplit[0]:useDCS(fSplit,cat)})
        return frame.CATss.values[0],data
    
ci = categoryInfo(cat)

#%%
tryThisMany = 5


reqs = []
i = 0
for n,g in gb:
    g = g.to_dict('records')
    g0 = g[0]
    g = g[1:]
    data = {
      "listing_sku": g0['sku'],
      "name": g0['webName'],
      "description": g0['description'],
      "category": categoryInfo(g0['DCSname'])[0],
      "brand": g0['BRAND'],
      "model": g0['name'],
      "accepts_offers": True,
      "ship_from_address_id": "6274eb59-120c-4de6-acba-8a5e193eb2b5",
      "images": [g0[f'image_{i}'] for i in range(5) if g0[f'image_{i}']],
      "length": 1,
      "width": 1,
      "height": 1,
      "weight": 1,
      "items": [
        {
          "item_sku": h['sku'],
          "quantity": h['qty'],
          "list_price": h['pSale'],
          "retail_price": h['pMSRP'],
          "ship_from_address_id": "6274eb59-120c-4de6-acba-8a5e193eb2b5",
          "gtin": h['UPC'],
          "mpn": h['mpn'],
          "images":[h[f'image_{i}'] for i in range(5) if h[f'image_{i}']],
          "length": 1,
          "width": 1,
          "height": 1,
          "weight": 1,
          "details": [
              [{'type':k,'option':h[v]} for k,v in ds[h['dcsname']].items()]
          ]
        } for h in g
      ]
    }
    res = postList(data)
    reqs.append(res)
    i += 1
    if i > tryThisMany-1:
        break
        break
#%% 

for r in reqs:
    print('CALL MADE\n')
    pprint(json.loads(r.request.body))
    print('\n', 'RESPONSE')
    pprint(json.loads(r.content))
    print('\n'+'-'*100+'\n')














