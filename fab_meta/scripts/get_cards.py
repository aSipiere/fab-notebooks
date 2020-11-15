import requests
import pandas as pd
import numpy as np


base_url = "https://api.fabdb.net/cards"


payload = {
    "page": 1,
    "per_page": 100,
}


def divide_chunks(n, d=100):
    return int((n+ (d-1))/d) + 1


pages = []
for i in range(1, divide_chunks(656, 100)):
    r = requests.get(base_url, params=payload)
    pages.append(r.json())
    print(r.json()['meta'])
    payload['page'] = i+1

dfs = []
for i in pages:
    dfs.append(pd.DataFrame.from_dict(i['data']))
df = pd.concat(dfs).reset_index()

stat_list = df.stats.values.tolist()
for n, i in enumerate(stat_list):
    if i == []:
        stat_list[n] = {}
        
df = df.drop(['stats', 'index'], axis=1).join(pd.DataFrame(stat_list))

def transform_name(row):

    resource_map = {
        '3': '(Blue)',
        '2': '(Yellow)',
        '1': '(Red)',
        np.nan: '',
    }
    
    return f"{row['name']} {resource_map[row['resource']]}"

df['name_resource'] = df.apply(transform_name, axis=1)

df = df[~df['identifier'].str.contains("IRA")]
df = df.drop_duplicates('name_resource')

df.to_csv("cards.csv", index=False)
