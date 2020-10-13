# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 09:36:36 2020

@author: Bagpyp

https://developer.sidelineswap.com/doc/index.html
"""

import json
import pandas as pd
pd.options.mode.chained_assignment=None
pd.options.display.max_rows = 150
pd.options.display.max_columns = 40
pd.options.display.width = 180
pd.options.display.max_colwidth = 40
# import pprint
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

df = pd.read_pickle(r'\\Server\c\Users\Administrator\RPBC2\ready.pkl')

catIDs = pd.json_normalize(json.loads(getCat().content))
details = pd.read_csv('category_detail_map.csv')
catMap = pd.read_csv('category_map.csv')
catFields = pd.read_csv('category_fields.csv')
        
catMap = catMap[catMap.uuid.notna()]
catMap.DCSname = catMap.DCSname.str.replace("'",'').str.lower()
catMap.CAT = catMap.CAT.str.replace("',",'')
catMap.uuid = catMap.uuid.str.replace('\\t','')

details.DCSname = details.DCSname.str.lower()
details = details[details.DCSname.isin(catMap.DCSname)]


