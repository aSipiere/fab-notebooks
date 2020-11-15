import pandas as pd
import streamlit as st

from fabdb_tools import *


st.title("FABTCG Meta")

st.markdown("""This is a prototype of a metagame analysis application for FABTCG.

All of this data is sourced from the [Tournament Decklists](https://fabtcg.com/decklists/) section of fabtcg.com.
There are currently not enough decks on the tournament list to support "Last x days" style groupings so the groupings are currently based on release.""")

releases = {
    "CRU": "./data/cru_decks.csv",
    "ARC": "./data/arc_decks.csv",
    "WTR": "./data/wtr_decks.csv",
}

release = st.sidebar.selectbox("Select a release:", list(releases.keys()))
decklists = pd.read_csv(releases[release])
decklists.dropna(inplace=True)
st.dataframe(decklists)

st.markdown("## Metagame Breakdown")
breakdown = get_meta_share(decklists)
breakdown['percentage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in breakdown['percentage']], index = breakdown.index)

st.dataframe(breakdown)

st.markdown('## Staples')
st.dataframe(get_staples(decklists))

st.markdown("This is a free  resource for the Flesh & Blood™ TCG by Legend Story Studios®. This is in no way affiliated with Legend Story Studios®. All intellectual IP belongs to Legend Story Studios®, Flesh & Blood™, and set names are trademarks of Legend Story Studios®. Flesh and Blood™ characters, cards, logos, and art are property of Legend Story Studios®. This is not a digital gaming product.")
