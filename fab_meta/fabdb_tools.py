import pandas as pd
import numpy as np
import requests


def get_deck(url):
    r = requests.get(url)
    soup = r.text
    frames = pd.read_html(url, flavor='bs4')
    
    metadata = {frames[0].iloc[:, 0].to_list()[i]: frames[0].iloc[:, 1].to_list()[i] for i in range(frames[0].shape[0])}
    equipment = frames[1].iloc[:, 0].str.extract("(?P<copies>.*?) x (?P<name>.*)")
    
    dfs = []
    for i in frames[2:]:
        dfs.append(i.iloc[:, 0].str.extract("(?P<copies>.*?) x (?P<name>.*) \((?P<resource>.*)\)"))    
    dfs.append(equipment)
    df = pd.concat(dfs)
    
    def transform_name(row):

        resource_map = {
            '3': '(Blue)',
            '2': '(Yellow)',
            '1': '(Red)',
            np.nan: '',
        }
        
        return f"{row['name']} {resource_map[row['resource']]}"
    
    df['name_resource'] = df.apply(transform_name, axis=1)
    
    # df = enrich_deck(df, card_df)
    # numeric_cols = ['copies', 'resource', 'attack', 'cost', 'defense', 'intellect', 'life']
    numeric_cols = ['copies', 'resource']

    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    
    return metadata, df


def enrich_deck(deck_df, card_df):
    return pd.merge(deck_df, card_df, left_on=['name_resource'], right_on=['name_resource'])


def add_decks_to_meta(meta_df):
    meta_list = meta_df.to_dict(orient='records')
    for i in meta_list:
        if i['deck_link'] is None:
            print("decklink is None")
        else:
            i['metadata'], i['deck'] = get_deck(i['deck_link'])
    
    return meta_list

def get_meta_share(df):
    hero_counts = df['Hero'].value_counts()
    hero_counts_df = pd.DataFrame({
        'hero': hero_counts.index, 
        'count': hero_counts,
        'percentage': hero_counts / hero_counts.sum()})

    return hero_counts_df

def count_card_group(group):
    
    # name = group.iloc[0]['name']
    total_copies = group['copies'].sum()
    if group[group['resource'] == 1].shape[0] > 0:
        red_copies = group[group['resource'] == 1].iloc[0]['copies']
    else:
        red_copies = 0
    if group[group['resource'] == 2].shape[0] > 0:
        yellow_copies = group[group['resource'] == 2].iloc[0]['copies']
    else:
        yellow_copies = 0
    if group[group['resource'] == 3].shape[0] > 0:
        blue_copies = group[group['resource'] == 3].iloc[0]['copies']
    else:
        blue_copies = 0

    return pd.DataFrame.from_dict({
        # 'name': name,
        'total_copies': [total_copies],
        'red_copies': [red_copies],
        'yellow_copies': [yellow_copies],
        'blue_copies': [blue_copies],
        })

def get_card_counts(deck, split_equipment=False):
    
    if split_equipment is False:
        counts = deck.groupby('name').apply(count_card_group)
        counts.reset_index(inplace=True)
        counts.drop('level_1', axis=1, inplace=True)

        return counts
    else:  # split_equipment is True
        pass

def get_staples_from_meta_list(meta_list):
    counts = []
    for i in meta_list:
        counts.append(get_card_counts(i['deck']))
    c_concat = pd.concat(counts)
    v_counts = c_concat['name'].value_counts().rename_axis('name').reset_index(name='decks')
    staples = c_concat.groupby('name').mean()
    staples = staples.merge(v_counts, how='outer', on="name")
    staples.rename(columns={"decks_x": "decks"}, inplace=True)
    staples.sort_values('decks', ascending=False, inplace=True)
    staples['percentage_of_decks'] = staples['decks'] / len(meta_list)

    return staples

def get_staples(df):
    meta_list = add_decks_to_meta(df)
    
    return get_staples_from_meta_list(meta_list)
 