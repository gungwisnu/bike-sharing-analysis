import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# konfig halaman dasar Streamlit
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

sns.set_theme(style="whitegrid")

# helper untuk memuat data bersih
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "main_data.csv")
    df = pd.read_csv(csv_path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

day_df = load_data()

# Filter sidebar
with st.sidebar:
    st.title("🚲 Bike Sharing")
    st.markdown("**Filter Data Penyewaan Sepeda**")

    min_date = day_df["dteday"].min().date()
    max_date = day_df["dteday"].max().date()

    date_range = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    season_list = day_df["season"].unique().tolist()
    selected_season = st.multiselect(
        label="Musim (Season)",
        options=season_list,
        default=season_list
    )

    weather_list = day_df["weathersit"].unique().tolist()
    selected_weather = st.multiselect(
        label="Kondisi Cuaca",
        options=weather_list,
        default=weather_list
    )

    st.divider()
    st.caption("Proyek Akhir Analisis Data\nAnak Agung Gede Wisnu Mahadhiva")

# proses rentang tanggal dari input sidebar
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

main_df = day_df[
    (day_df["dteday"].dt.date >= start_date) &
    (day_df["dteday"].dt.date <= end_date) &
    (day_df["season"].isin(selected_season)) &
    (day_df["weathersit"].isin(selected_weather))
]

# header dan matrik utama
st.title("📊 Bike Sharing Analytics Dashboard")
st.markdown(f"Menampilkan performa penyewaan sepeda dari **{start_date}** hingga **{end_date}**.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Penyewaan", value=f"{main_df['cnt'].sum():,}")
with col2:
    st.metric(label="Total Registered", value=f"{main_df['registered'].sum():,}")
with col3:
    st.metric(label="Total Casual", value=f"{main_df['casual'].sum():,}")
with col4:
    avg_rent = main_df["cnt"].mean() if not main_df.empty else 0
    st.metric(label="Rata-rata Harian", value=f"{avg_rent:,.0f} / hari")

st.divider()

# visualisasi pertanyaan 1 tren bulanan dan musim
st.subheader("1. Tren Pertumbuhan Bulanan & Performa Musiman")
col_left, col_right = st.columns([1.35, 1])

with col_left:
    fig, ax = plt.subplots(figsize=(10, 5))
    if not main_df.empty:
        monthly_df = main_df.resample("ME", on="dteday")["cnt"].sum().reset_index()
        sns.lineplot(
            data=monthly_df, x="dteday", y="cnt",
            marker="o", linewidth=2.5, color="#0D47A1", ax=ax
        )
    ax.set_title("Tren Total Penyewaan Sepeda Bulanan", fontsize=13, fontweight="bold")
    ax.set_xlabel("Bulan", fontsize=11)
    ax.set_ylabel("Total Penyewaan", fontsize=11)
    plt.xticks(rotation=30)
    sns.despine()
    st.pyplot(fig)

with col_right:
    fig, ax = plt.subplots(figsize=(8, 5))
    if not main_df.empty:
        season_df = main_df.groupby("season")["cnt"].mean().sort_values(ascending=False).reset_index()
        colors_s = ["#0D47A1" if x == season_df["cnt"].max() else "#D3D3D3" for x in season_df["cnt"]]
        sns.barplot(
            data=season_df, x="cnt", y="season",
            palette=colors_s, hue="season", legend=False, ax=ax
        )
        for i, v in enumerate(season_df["cnt"]):
            ax.text(v + 50, i, f"{v:,.0f}", va="center", fontweight="bold")
        ax.set_xlim(0, season_df["cnt"].max() * 1.18)
    ax.set_title("Rata-rata Penyewaan Harian Berdasarkan Musim", fontsize=13, fontweight="bold")
    ax.set_xlabel("Rata-rata Penyewaan Harian", fontsize=11)
    ax.set_ylabel("Musim", fontsize=11)
    sns.despine()
    st.pyplot(fig)

st.divider()

# visualisasi pertanyaan 2 dan analisis lanjutan
st.subheader("2. Perilaku Segmen Pengguna & Analisis Lanjutan (Clustering Suhu)")
col_b1, col_b2 = st.columns(2)

with col_b1:
    fig, ax = plt.subplots(figsize=(8, 5))
    if not main_df.empty:
        wd_df = main_df.groupby("workingday")[["registered", "casual"]].mean().reset_index()
        wd_melted = wd_df.melt(
            id_vars="workingday", var_name="Segmen Pengguna", value_name="Rata-rata Penyewaan"
        )
        sns.barplot(
            data=wd_melted, x="workingday", y="Rata-rata Penyewaan",
            hue="Segmen Pengguna", palette=["#0D47A1", "#FF9800"], ax=ax
        )
    ax.set_title("Rata-rata Penyewaan: Working Day vs Holiday/Weekend", fontsize=12, fontweight="bold")
    ax.set_xlabel("Kategori Hari", fontsize=11)
    ax.set_ylabel("Rata-rata Penyewaan Harian", fontsize=11)
    sns.despine()
    st.pyplot(fig)

with col_b2:
    fig, ax = plt.subplots(figsize=(8, 5))
    if not main_df.empty and "temp_cluster" in main_df.columns:
        order_temp = ["Cold (<15°C)", "Mild/Ideal (15-25°C)", "Warm/Hot (>25°C)"]
        temp_df = main_df.groupby("temp_cluster")["cnt"].mean().reindex(order_temp).fillna(0).reset_index()
        colors_t = ["#0D47A1" if x == temp_df["cnt"].max() and x > 0 else "#D3D3D3" for x in temp_df["cnt"]]
        sns.barplot(
            data=temp_df, x="temp_cluster", y="cnt",
            palette=colors_t, hue="temp_cluster", legend=False, ax=ax
        )
        for i, v in enumerate(temp_df["cnt"]):
            ax.text(i, v + 80, f"{v:,.0f}", ha="center", fontweight="bold")
        if temp_df["cnt"].max() > 0:
            ax.set_ylim(0, temp_df["cnt"].max() * 1.18)
    ax.set_title("Rata-rata Penyewaan Berdasarkan Klaster Suhu (Binning)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Klaster Suhu Udara (°C)", fontsize=11)
    ax.set_ylabel("Rata-rata Penyewaan Harian", fontsize=11)
    sns.despine()
    st.pyplot(fig)