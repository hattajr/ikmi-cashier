import streamlit as st
import polars as pl



data = pl.read_csv("price.csv")
print(data)
items = st.multiselect(
    "Beli apa",
    data["items"].sort().to_list(),
    default=["Abc kopi"])


total_cost=0
for ix,i in enumerate(items):
    with st.container(height=100):
        item_col, price_col, amount_col, total_col = st.columns(4, vertical_alignment="center")
        item_col.write(i)
        price = data.filter(pl.col("items") == i).item(0,"price") 
        price_col.write(price)
        amount = amount_col.number_input("Jumlah", value=1, key=i, label_visibility="hidden",min_value=1)
        total_cost_ = price * amount 
        total_col.write(total_cost_)
        total_cost += total_cost_

st.write(f"**Total: {total_cost}**")

