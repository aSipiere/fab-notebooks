import re
import argparse
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np


def get_number_of_pages():
    r = requests.get(f"https://fabtcg.com/decklists/?page=1")
    soup = BeautifulSoup(r.text, 'html.parser')
    last = int(soup.findAll("a", {"class": "page-link starling"})[-1]['href'].partition("=")[-1])
    return last


def get_page(page):
    r = requests.get(f"https://fabtcg.com/decklists/?page={page}")
    soup = BeautifulSoup(r.text, 'html.parser')
    
    df = pd.read_html(f"https://fabtcg.com/decklists/?page={page}", flavor='bs4')[0]
    
    table = soup.find('table')
    links = {}
    for tr in table.findAll("tr"):
        trs = tr.findAll("td")
        for each in trs:
            try:
                a_text = re.sub('\s+',' ', each.find('a').contents[0])
                a_link = each.find('a')['href']
                links[a_text] = a_link
            except:
                pass

    def fetch_deck_url(row):
        try:
            deck = links[row['Decklist']]
        except:
            deck = None

        return deck

    def fetch_event_url(row):
        try:
            event = links[row['Event']]
        except:
            event = None

        return event
    
    df['deck_link'] = df.apply(fetch_deck_url, axis=1)
    df['event_link'] = df.apply(fetch_event_url, axis=1)
    df['Date'] = pd.to_datetime(df['Date'])
    
    return df

def get_all_pages():
    dfs = []
    for i in range(1, get_number_of_pages()):
        dfs.append(get_page(i))
        
    return pd.concat(dfs).reset_index(drop=True)



releases = {
    'CRU': ('2020-08-28', datetime.now().strftime("%Y-%m-%d")),
    'ARC': ('2020-03-27', '2020-08-28'),
    'WTR': ('1970-01-01', '2020-03-27'),
    'ALL': ('1970-01-01', datetime.now().strftime("%Y-%m-%d")),
}


def get_meta(df, date_tuple, tournament_format):
    return df[
        (df['Format'] == tournament_format) 
        & (df['Date'] >= date_tuple[0])
        & (df['Date'] < date_tuple[1])
        ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--card-db', '-c', help='File path to card csv')
    parser.add_argument('--release', '-r', help='Identifier string of set. E.g. WTR, ARC, ALL.')
    parser.add_argument('--output', '-o', help='Path to output file.')

    args = parser.parse_args()
    
    df = get_all_pages()
    card_df = pd.read_csv(args.card_db).drop(['image', 'resource', 'name'], axis=1)
    meta_df = get_meta(df, date_tuple=releases[args.release], tournament_format="CC")
    meta_df.to_csv(args.output, index=False)