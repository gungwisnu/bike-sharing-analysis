# Bike Sharing Analytics Dashboard

Proyek analisis data dan pengembangan dashboard interaktif menggunakan Bike Sharing Dataset (2011–2012)[cite: 1, 5, 10].

## Struktur Direktori

```text
submission
├───dashboard
│   ├───main_data.csv
│   └───dashboard.py
├───data
│   ├───day.csv
│   └───hour.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment - Anaconda / Miniconda

```bash
conda create --name main-ds python=3.10
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell / Terminal

```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App

```bash
streamlit run dashboard/dashboard.py
```