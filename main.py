import os

import polars as pl
import requests
import streamlit as st
import toml

CONFIG_FILEPATH = "config.toml"
PRICE_FILEPATH = "price_test.csv"
TTL_CACHE = 60 * 15

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

if "selection" not in st.session_state:
    st.session_state.selection = None

if "var_list" not in st.session_state:
    st.session_state["var_list"] = []


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


def clear_selectbox():
    code = st.session_state.selection
    if code:
        produk = data.filter(pl.col("Barcode") == code).item(0, "Produk")
        st.info(f"**{produk}** berhasil ditambahkan.")
        st.session_state.var_list.append(
            {
                code: {
                    "produk": produk,
                    "harga": data.filter(pl.col("Barcode") == code).item(0, "Harga"),
                }
            }
        )
    st.session_state.selection = None


# var_list_copy = copy.deepcopy(st.session_state.var_list)

code = st.selectbox(
    ":label: **Barang/Items:**",
    options=data["Barcode"].sort().to_list(),
    index=None,
    format_func=lambda option: f'{data.filter(pl.col("Barcode") == option).item(0, "Produk")} - {option}',
    key="selection",
    on_change=clear_selectbox(),
)

total_cost = 0
total_item = 0
items = {}
for ix, item in enumerate(st.session_state.var_list):
    for key, value in item.items():
        if key in items:
            items[key]["count"] += 1
        else:
            items[key] = {
                "harga": value["harga"],
                "produk": value["produk"],
                "count": 1,
            }

for ix, (k, v) in enumerate(items.items()):
    with st.container(height=250):
        produk_name = v["produk"]
        price = v["harga"]
        image_path = f"images/{produk_name}.png"
        if os.path.exists(image_path):
            st.image(image_path, width=100)
        else:
            st.image("images/no_image.jpg", width=100)
        amount = st.number_input(
            f"{produk_name} `₩{price}`", value=v["count"], key=ix, min_value=1
        )
        total_item += amount
        total_cost_ = price * amount
        st.markdown(f"`₩{price} x {amount} = ₩{total_cost_}`")
        total_cost += total_cost_

st.success(f"""
    **Jumlah Barang : {total_item:,}**\n
    **Total Harga (₩): {total_cost:,}**
""")
