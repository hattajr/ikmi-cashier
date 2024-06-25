import streamlit as st
import os
import polars as pl
import requests
import toml

st.set_page_config(layout="wide")


def load_price_local():
    data = pl.read_csv("price.csv", truncate_ragged_lines=True)
    return data.with_columns(pl.col("Harga").str.strip_chars().cast(int)).drop_nulls()

@st.cache_data
def load_price_gsheets():
    with open('secret.toml', 'r') as file:
        secret = toml.load(file)
    response = requests.get(f'https://docs.google.com/spreadsheets/d/{secret["gsheets"]["sheet_id"]}/export?format=csv')
    with open('prices_gsheet.csv', 'wb') as f:
        f.write(response.content)
    data = pl.read_csv("prices_gsheet.csv")
    return data

data = load_price_gsheets()
print(data)
st.title("TEST")
items = st.multiselect(
    ":label: **Barang/Items:**",
    data["Produk"].sort().to_list(),
    default=None,
)


total_cost=0
for ix,i in enumerate(items):
    with st.container(height=250):
        price = data.filter(pl.col("Produk") == i).item(0,"Harga") 
        image_path = f"images/{i}.png"
        if os.path.exists(image_path):
            st.image(image_path, width=100)
        else: 
            st.image("images/no_image.jpg", width=100)
        amount = st.number_input(f"{i} `₩{price}`", value=1, key=i ,min_value=1)
        total_cost_ = price * amount 
        st.markdown(f"`₩{price} x {amount} = ₩{total_cost_}`")
        total_cost += total_cost_

st.info(f"**Total(₩): {total_cost:,}**")

