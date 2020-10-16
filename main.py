# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:14:12 2020

@author: Bagpyp
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
              categoryInfo(g0['DCSname'])[1]
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

