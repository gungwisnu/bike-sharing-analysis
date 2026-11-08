import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Dashboard Penyewaan Sepeda", layout="wide")
sns.set_style("whitegrid")

@st.cache_data
def baca_data():
    folder_ini = os.path.dirname(os.path.abspath(__file__))
    lokasi_csv = os.path.join(folder_ini, "main_data.csv")
    data = pd.read_csv(lokasi_csv)
    data["dteday"] = pd.to_datetime(data["dteday"])
    return data

df = baca_data()

with st.sidebar:
    st.header("Filter Data")
    tgl_awal = df["dteday"].min().date()
    tgl_akhir = df["dteday"].max().date()

    rentang_tgl = st.date_input(
        "Pilih Rentang Tanggal",
        min_value=tgl_awal,
        max_value=tgl_akhir,
        value=[tgl_awal, tgl_akhir]
    )

    pilihan_musim = df["season"].unique().tolist()
    filter_musim = st.multiselect("Musim", options=pilihan_musim, default=pilihan_musim)

    pilihan_cuaca = df["weathersit"].unique().tolist()
    filter_cuaca = st.multiselect("Kondisi Cuaca", options=pilihan_cuaca, default=pilihan_cuaca)

    st.caption("Oleh: Anak Agung Gede Wisnu Mahadhiva")

if len(rentang_tgl) == 2:
    mulai, selesai = rentang_tgl
else:
    mulai, selesai = tgl_awal, tgl_akhir

df_filter = df[
    (df["dteday"].dt.date >= mulai) &
    (df["dteday"].dt.date <= selesai) &
    (df["season"].isin(filter_musim)) &
    (df["weathersit"].isin(filter_cuaca))
]

st.title("Dashboard Analisis Penyewaan Sepeda (2011 - 2012)")
st.write(f"Data ditampilkan untuk rentang **{mulai}** sampai **{selesai}**.")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Penyewaan", f"{df_filter['cnt'].sum():,}")
k2.metric("Pelanggan Registered", f"{df_filter['registered'].sum():,}")
k3.metric("Pengguna Casual", f"{df_filter['casual'].sum():,}")
rata_harian = df_filter["cnt"].mean() if not df_filter.empty else 0
k4.metric("Rata-rata per Hari", f"{rata_harian:,.0f}")

st.divider()

tab1, tab2 = st.tabs(["Cuaca, Musim & Tren Bulanan", "Kategori Hari & Kelembapan Udara"])

with tab1:
    st.subheader("Tren Bulanan serta Pengaruh Cuaca dan Musim")
    fig1, ax1 = plt.subplots(figsize=(12, 4))
    if not df_filter.empty:
        rekap_bulanan = df_filter.resample("ME", on="dteday")["cnt"].sum().reset_index()
        sns.lineplot(data=rekap_bulanan, x="dteday", y="cnt", marker="o", color="#2b5c8f", linewidth=2.2, ax=ax1)
    ax1.set_title("Total Penyewaan per Bulan")
    ax1.set_xlabel("Bulan")
    ax1.set_ylabel("Jumlah Sewa")
    sns.despine()
    st.pyplot(fig1)

    c_kiri, c_kanan = st.columns(2)
    with c_kiri:
        fig2, ax2 = plt.subplots(figsize=(7, 4.5))
        if not df_filter.empty:
            df_cuaca = df_filter.groupby("weathersit")["cnt"].mean().sort_values(ascending=False).reset_index()
            warna_c = ["#2b5c8f" if x == df_cuaca["cnt"].max() else "#cbd5e1" for x in df_cuaca["cnt"]]
            sns.barplot(data=df_cuaca, x="weathersit", y="cnt", palette=warna_c, hue="weathersit", legend=False, ax=ax2)
        ax2.set_title("Rata-rata Sewa Harian Berdasarkan Cuaca")
        ax2.set_xlabel("Kondisi Cuaca")
        ax2.set_ylabel("Rata-rata Sewa")
        sns.despine()
        st.pyplot(fig2)

    with c_kanan:
        fig3, ax3 = plt.subplots(figsize=(7, 4.5))
        if not df_filter.empty:
            df_musim = df_filter.groupby("season")["cnt"].mean().sort_values(ascending=False).reset_index()
            warna_m = ["#2b5c8f" if x == df_musim["cnt"].max() else "#cbd5e1" for x in df_musim["cnt"]]
            sns.barplot(data=df_musim, x="cnt", y="season", palette=warna_m, hue="season", legend=False, ax=ax3)
        ax3.set_title("Rata-rata Sewa Harian Berdasarkan Musim")
        ax3.set_xlabel("Rata-rata Sewa")
        ax3.set_ylabel("Musim")
        sns.despine()
        st.pyplot(fig3)

with tab2:
    st.subheader("Perbandingan Hari Kerja vs Libur & Binning Kelembapan")
    b_kiri, b_kanan = st.columns(2)

    with b_kiri:
        fig4, ax4 = plt.subplots(figsize=(7, 4.5))
        if not df_filter.empty:
            df_hari = df_filter.groupby("workingday")[["registered", "casual"]].mean().reset_index()
            df_melt = df_hari.melt(id_vars="workingday", var_name="Tipe", value_name="Rata_Sewa")
            sns.barplot(data=df_melt, x="workingday", y="Rata_Sewa", hue="Tipe", palette=["#2b5c8f", "#e07a5f"], ax=ax4)
        ax4.set_title("Rata-rata Sewa: Hari Kerja vs Libur/Akhir Pekan")
        ax4.set_xlabel("Jenis Hari")
        ax4.set_ylabel("Rata-rata Harian")
        sns.despine()
        st.pyplot(fig4)

    with b_kanan:
        fig5, ax5 = plt.subplots(figsize=(7, 4.5))
        if not df_filter.empty and "hum_group" in df_filter.columns:
            urut_h = ["Kering (<50%)", "Ideal (50-75%)", "Lembap (>75%)"]
            df_hum = df_filter.groupby("hum_group")["cnt"].mean().reindex(urut_h).fillna(0).reset_index()
            warna_h = ["#2b5c8f" if x == df_hum["cnt"].max() and x > 0 else "#cbd5e1" for x in df_hum["cnt"]]
            sns.barplot(data=df_hum, x="hum_group", y="cnt", palette=warna_h, hue="hum_group", legend=False, ax=ax5)
        ax5.set_title("Rata-rata Sewa Berdasarkan Kategori Kelembapan")
        ax5.set_xlabel("Kelompok Kelembapan Udara")
        ax5.set_ylabel("Rata-rata Harian")
        sns.despine()
        st.pyplot(fig5)