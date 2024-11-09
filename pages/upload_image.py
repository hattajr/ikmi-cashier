import streamlit as st
import polars as pl
import os
import time
from streamlit import caching

caching.clear_cache()

st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

PRICE_FILEPATH = "price_test.csv"



if os.path.exists(PRICE_FILEPATH):
    data = pl.read_csv(PRICE_FILEPATH)
    data = data.with_columns(pl.col("Harga").cast(pl.Int64))
    produk = st.selectbox("Pilih nama produk", data["Produk"].to_list(), index=None, key="produk")
    st.write("`If you can not find the product name, please update it in GSheet`")

if produk:
    picture = st.camera_input("Gambar Produk")

if produk and picture:
    if st.button("Submit"):
        with open (f'images/{produk}.jpg','wb') as file:
            file.write(picture.getbuffer())
        st.success("Gambar berhasil disimpan :)")
        time.sleep(0.3)
        st.rerun()

