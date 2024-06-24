import streamlit as st
import os
import polars as pl
from streamlit_tags import st_tags



@st.cache_data
def load_price():
    data = pl.read_csv("price.csv")
    return data

data = load_price()
st.title("IKMI MART CALCULATOR")
items = st.multiselect(
    ":label: **Barang/Items:**",
    data["items"].sort().to_list(),
    default=["Abc kopi"],
)



total_cost=0
for ix,i in enumerate(items):
    with st.container(height=230):
        price = data.filter(pl.col("items") == i).item(0,"price") 
        image_path = f"images/{i}.png"
        if os.path.exists(image_path):
            st.image(image_path, width=100)
        else: 
            st.image("images/no_image.jpg", width=100)
        amount = st.number_input(f"{i} `₩{price:,}`", value=1, key=i ,min_value=1)
        total_cost_ = price * amount 
        st.markdown(f"`₩{price:,} x {amount} = ₩{total_cost_:,}`")
        total_cost += total_cost_

st.info(f"**Total(₩): {total_cost:,}**")

