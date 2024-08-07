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


if "shopping_list" not in st.session_state:
    st.session_state["shopping_list"] = {}


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
        if code in st.session_state.shopping_list.keys():
            if st.session_state.shopping_list[code]["count"] >= 1:
                st.error(f"{produk} telah dinput")
        else:
            st.session_state.shopping_list.update(
                {
                    code: {
                        "produk": produk,
                        "harga": data.filter(pl.col("Barcode") == code).item(
                            0, "Harga"
                        ),
                        "count": 1,
                    }
                }
            )

    st.session_state.selection = None


code_input = st.selectbox(
    ":label: **Barang/Items:**",
    options=data["Barcode"].sort().to_list(),
    index=None,
    format_func=lambda option: f'{data.filter(pl.col("Barcode") == option).item(0, "Produk")} - {option}',
    key="selection",
    on_change=clear_selectbox(),
)

total_cost = 0
total_item = 0

for ix, (code, details) in enumerate(st.session_state.shopping_list.copy().items()):
    with st.container(height=300):
        produk_name = details["produk"]
        price = details["harga"]
        image_path = f"images/{produk_name}.png"
        if os.path.exists(image_path):
            st.image(image_path, width=100)
        else:
            st.image("images/no_image.jpg", width=100)

        amount = st.number_input(
            f"{produk_name} `₩{price}`",
            value=details["count"],
            min_value=0,
        )
        total_item += amount
        total_cost_ = price * amount
        st.markdown(f"`₩{price} x {amount} = ₩{total_cost_}`")
        total_cost += total_cost_
        
        is_delete = st.button("delete", key=ix)
        if is_delete:
            del st.session_state.shopping_list[code]



st.success(f"""
    **Jumlah Barang : {total_item:,}**\n
    **Total Harga (₩): {total_cost:,}**
""")
