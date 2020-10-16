# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:14:12 2020

@author: Bagpyp
"""

import json
from numpy import nan,where
import pandas as pd
pd.options.mode.chained_assignment=None
pd.options.display.max_rows = 150
pd.options.display.max_columns = 40
pd.options.display.width = 180
pd.options.display.max_colwidth = 40
import requests

from datetime import datetime as dt

def log(text, stamp=False, base='log'):
    with open(f"logs/{base} {dt.now().strftime('%d-%m-%Y')}.txt", 'a') as file:
        if stamp:
            file.write(f"\n\n\n{dt.now().strftime('%H:%M:%S')}\n\n")
        file.write(text)
        file.write('\n')   

#%%

with open('apiKey.txt') as file:
    a = file.readline()
    b = file.readline()

base = 'https://developer.sidelineswap.com/v1/'
headers = {'x-api-key':a,
           'x-client-id':b,
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

# res = setAddress({'street_1': '2424 SE Burnside Rd',
#   'city': 'Gresham',
#   'state': 'OR',
#   'zip': '97080',
#   'country': 'US'})

# if res.ok:
#     print('address set')


#%%
    
cmap = pd.read_csv('cat_map.csv')
det = pd.read_csv('detail_map.csv')

for df in [cmap,det]:
    df.dcsname = df.dcsname.str.replace('hike/pack','hike, pack')

cmap = cmap[cmap.uuid.notna()]
det = det[det.dcsname.isin(cmap.dcsname)]

c = cmap.set_index('dcsname').cat.to_dict()

det['dic'] = det.detail.fillna('')+':'+det.field.fillna('')

#comment out BEGIN to test locally
df = pd.read_pickle(r'\\Server\c\Users\Administrator\RPBC2\ready.pkl')\
    .reset_index()\
    .replace({nan:None})\
    .drop(['fCreated','lModified','p_date_created','p_date_modified'], axis = 1)
df['dcsname'] = df.DCSname.str.replace('Hike/Pack','Hike, Pack').str.lower()
df = df[df.dcsname.isin(list(c.keys()))]
df[list('dcs')] = df.dcsname.str.split('/',expand=True)
df['cond'] = where(df.DCSname.str.contains('clearance'),\
                   'used','new')
df.webName = where(df.webName.str.split(' ')\
                   .apply(lambda x: len(x)) == 2,
                   'New: '+df.webName, \
                   df.webName)
    
df.webName = where(df.webName.str.split(' ')\
                   .apply(lambda x: len(x)) == 1,
                   'From Hillcrest: '+df.webName, \
                   df.webName)    
#comment out END to test locally
df.to_pickle('currentDf.pkl')

#comment out BEGIN to run
# df = pd.read_pickle('currentDf.pkl')
#comment our END to run

#%%
req = pd.read_csv('category_fields.csv')
fields = {n:f.field.unique().tolist() \
          for n,f in req.groupby('catname', sort=False)}

# print(req.head())
#%%


    
db = det[['dcsname','dic']].groupby('dcsname',sort=False)
# ds does not contain 'safety/helmet/ski' as key - fixed
# ds does not contain 'rental/ski/binding' as key....

ds = {}
for n,d in db:
    dl = d.dic.values.tolist()
    kvs = {s.split(':')[0]:s.split(':')[1] for s in dl}
    kvs.update({'Condition':'cond'})
    ds.update({n:kvs})
for k in list(c.keys()):
    if k not in ds:
        ds.update({k:{'Condition':'cond'}})




#%%
gb = df.groupby('webName', sort=False)
failures= []
reqs = []
N = gb.ngroups
for i,(n,g) in enumerate(gb):
    print(f'{i}/{N}')
    g = g.to_dict('records')
    g0 = g[0]
    if len(g)>1:
        g = g[1:]
    else:
        g = [g0.copy()]
    cat = c[g0['dcsname']]
    
    data = {
      "listing_sku": g0['sku'],
      "name": g0['webName'],
      "description": g0['description'],
      "category": cat,
      "brand": g0['BRAND'],
      "model": g0['name'],
      "accepts_offers": True,
      "ship_from_address_id": "db4f7b6a-91d8-4fbb-806a-d07e7449f5e2",
      "images": [g0[f'image_{i}'] for i in range(5) if g0[f'image_{i}']],
      # omit
      "length": 5,
      "width": 5,
      "height": 5,
      "weight": 5,      
      "items": [
        {
          "item_sku": h['sku'],
          "quantity": h['qty'],
          "list_price": h['pSale'],
          "retail_price": h['pMSRP'],
          "gtin": h['UPC'],
          "mpn": h['mpn'],
          "images":[h[f'image_{i}'] for i in range(5) if h[f'image_{i}']],
          "details": [{'type':k,'option':h[v]} for k,v in ds[h['dcsname']].items()]
        } for h in g
      ]
    }
    for h in data['items']:
        # print('original details',h['details'])
        if cat in fields:
            want = fields[cat]
        else:
            want = []
        have = [detail['type'] for detail in h['details']]
        need = [x for x in want if x not in have]
        # if Size ends up in need, just grab if from h!!!
        h['details'].extend([{'type':n,'option':'other'} for n in need])
    res = postList(data)

    if res.status_code != 200:
        failures.append(res)
    else:
        reqs.append(res)
        
        
        
log("FAILURES", stamp=True, base='failureLog')
for i,f in enumerate(failures):
    logtext = '\n'+'-'*100+f'\n\n{i}\n\n' \
        + json.dumps(json.loads(f.content)) \
        + '\n\n' \
        + json.dumps(json.loads(f.request.body)) \
        + '\n\n'
    log(logtext, base='failureLog')
            
    
    
#%%

# for h in data['items']:
#     print('original details',h['details'])
#     want = fields[data['category']]
#     print('want: ', want)
#     have = [detail['type'] for detail in h['details']]
#     print('\thave: ',have)
#     need = [x for x in want if x not in have]
#     print('\t\tneed: ',need)
#     h['details'].extend([{'type':n,'option':'other'} for n in need])
#     print('fixed details',h['details'],'\n')
    
#%% 

# for r in reqs:
#     print('CALL MADE\n')
#     pprint(json.loads(r.request.body))
#     print('\n', 'RESPONSE')
#     pprint(json.loads(r.content))
#     print('\n'+'-'*100+'\n')

