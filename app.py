import streamlit as st
import pandas as pd
import itertools
from io import BytesIO

st.set_page_config(page_title="Web Dashboard ML", layout="wide")

df = pd.read_csv("Data/algoritma_kmeans.csv")

st.title("Web Dashboard Analisis Konten")

menu = st.sidebar.selectbox(
    "Menu",
    ["Beranda", "Kategori", "Trending"]
)

if menu == "Beranda":
    hashtags_series = (
        df["hashtag"]
        .dropna()
        .astype(str)
        .str.lower()
        .str.split()
    )

    all_hashtags = list(itertools.chain.from_iterable(hashtags_series))

    top_hashtags = (
        pd.Series(all_hashtags)
        .value_counts()
        .head(10)
    )

    rekom_hashtags = [
        h[1:] if h.startswith("#") else h
        for h in top_hashtags.index.tolist()[:5]
    ]

    top_music = (
        df["music_track"]
        .dropna()
        .value_counts()
        .head(10)
    )

    df["upload_time"] = pd.to_datetime(df["upload_time"], errors="coerce")

    best_hours = (
        df.dropna(subset=["upload_time"])
        .assign(hour=lambda x: x["upload_time"].dt.hour)
        .groupby("hour")["engagement_rate"]
        .mean()
        .sort_values(ascending=False)
        .head(3)
        .index.tolist()
    )

    best_hours_label = [f"{h:02d}.00 WIB" for h in best_hours]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Hashtag")
        st.bar_chart(top_hashtags)

    with col2:
        st.subheader("Top Music")
        st.bar_chart(top_music)

    st.subheader("Rekomendasi")
    st.write("Hashtag:", rekom_hashtags)
    st.write("Music:", top_music.index.tolist()[:5])
    st.write("Jam Upload Terbaik:", best_hours_label)

    st.divider()
    st.subheader("Upload Data User")

    template = pd.DataFrame(columns=[
        "hashtag", "music_track", "views",
        "likes", "comments", "shares", "upload_time"
    ])

    buffer = BytesIO()
    template.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        "Download Template Excel",
        data=buffer,
        file_name="template_input.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx"])

    if uploaded_file:
        df_user = pd.read_excel(uploaded_file)

        df_user["engagement_rate"] = (
            df_user["likes"] +
            df_user["comments"] +
            df_user["shares"]
        ) / df_user["views"]

        df_user["upload_time"] = pd.to_datetime(
            df_user["upload_time"], errors="coerce"
        )

        user_hashtags = (
            df_user["hashtag"]
            .value_counts()
            .head(5)
            .index
            .tolist()
        )

        user_music = (
            df_user["music_track"]
            .value_counts()
            .head(5)
            .index
            .tolist()
        )

        user_best_hour = (
            df_user.dropna(subset=["upload_time"])
            .assign(hour=lambda x: x["upload_time"].dt.hour)
            .groupby("hour")["engagement_rate"]
            .mean()
            .idxmax()
        )

        st.success("Data berhasil diproses")
        st.write("Hashtag Teratas:", user_hashtags)
        st.write("Music Teratas:", user_music)
        st.write("Jam Terbaik Upload:", f"{user_best_hour:02d}.00 WIB")

elif menu == "Kategori":
    kategori = st.selectbox(
        "Pilih Kategori",
        ["kuliner", "fashion", "kecantikan", "teknologi"]
    )

    KATEGORI_MAP = {
        "kuliner": ["kuliner", "makanan", "food"],
        "fashion": ["fashion", "ootd", "outfit"],
        "kecantikan": ["skincare", "makeup", "beauty"],
        "teknologi": ["teknologi", "gadget", "tech"]
    }

    keywords = KATEGORI_MAP[kategori]

    df_kategori = df[
        df["hashtag"]
        .astype(str)
        .str.lower()
        .str.contains("|".join(keywords), na=False)
    ]

    hashtags_series = (
        df_kategori["hashtag"]
        .dropna()
        .astype(str)
        .str.lower()
        .str.split()
    )

    all_hashtags = list(itertools.chain.from_iterable(hashtags_series))

    top_hashtags = (
        pd.Series(all_hashtags)
        .value_counts()
        .head(10)
    )

    top_music = (
        df_kategori["music_track"]
        .dropna()
        .value_counts()
        .head(5)
    )

    st.subheader(f"Kategori: {kategori}")
    st.bar_chart(top_hashtags)
    st.bar_chart(top_music)

elif menu == "Trending":
    top_hashtags = df["hashtag"].value_counts().head(10)
    top_music = df["music_track"].value_counts().head(10)

    st.subheader("Trending Hashtag")
    st.bar_chart(top_hashtags)

    st.subheader("Trending Music")
    st.bar_chart(top_music)
