import os

import polars as pl
import requests
import streamlit as st
import toml

CONFIG_FILEPATH = "config.toml"
PRICE_FILEPATH = "prices.csv"
TTL_CACHE = 60 * 15

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


def get_price_gsheets():
    with open(CONFIG_FILEPATH, "r") as file:
        config = toml.load(file)
    response = requests.get(
        f'https://docs.google.com/spreadsheets/d/{config["gsheets"]["sheet_id"]}/export?format=csv'
    )
    with open(PRICE_FILEPATH, "wb") as f:
        f.write(response.content)
    return


@st.cache_data(ttl=TTL_CACHE, show_spinner=False)
def load_price_local():
    if not os.path.exists(PRICE_FILEPATH):
        st.info("get gsheets")
        get_price_gsheets()
    data = pl.read_csv(PRICE_FILEPATH).drop_nulls()
    return data


st.title("IKMI MART CALCULATOR")

with st.sidebar:
    is_update = st.button("Update Database")
    if is_update:
        try:
            os.remove(PRICE_FILEPATH)
        except FileNotFoundError:
            pass
        except Exception as e:
            st.error(e)
        finally:
            st.cache_data.clear()
            get_price_gsheets()
            st.info("Database is updated")


data = load_price_local()
items = st.multiselect(
    ":label: **Barang/Items:**",
    data["Produk"].sort().to_list(),
    default=None,
)


total_cost = 0
total_item = 0
for ix, i in enumerate(items):
    with st.container(height=250):
        price = data.filter(pl.col("Produk") == i).item(0, "Harga")
        image_path = f"images/{i}.png"
        if os.path.exists(image_path):
            st.image(image_path, width=100)
        else:
            st.image("images/no_image.jpg", width=100)
        amount = st.number_input(f"{i} `₩{price}`", value=1, key=i, min_value=1)
        total_item += amount
        total_cost_ = price * amount
        st.markdown(f"`₩{price} x {amount} = ₩{total_cost_}`")
        total_cost += total_cost_

st.success(f"""
    **Jumlah Barang : {total_item:,}**\n
    **Total Harga (₩): {total_cost:,}**
""")
st.info("398-910531-91007 APRILIYANTO FADA HANA BANK")