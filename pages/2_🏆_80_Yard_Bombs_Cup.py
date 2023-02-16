import streamlit as st
from snowflake.snowpark import Session
from global_functions import get_session

session = get_session()

with st.spinner('Checking the trophy room!'):
    st.write('## 🏆 The Race For The 80 Yard Bombs Cup')

    cup_standings_df = session.table('cup_standings')


    st.dataframe(cup_standings_df)