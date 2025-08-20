
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Vertriebsfolgeprovisionen", layout="wide")
st.title("📊 Vertriebsfolgeprovisionen Berechnungstool")

st.markdown("""
Dieses Tool berechnet auf Basis deiner Fonds-Holdings und NAV-Dateien die monatliche Vertriebsfolgeprovision in der Fondswährung.

🔹 **Fixe Basispunkte:** 60 bps  
🔹 **Berechnung:**  
\[
\text{Provision} = (NAV \times Units) \times \frac{60}{10\,000} \div 12
\]
""", unsafe_allow_html=True)

# Datei-Uploads
holdings_file = st.file_uploader("🔼 Lade die Holdings-Datei hoch (.xlsx)", type=["xlsx"])
nav_file = st.file_uploader("🔼 Lade die NAV-Datei hoch (.xlsx)", type=["xlsx"])
bps_input = st.number_input(
    "📉 Höhe der Vertriebsprovision in Basispunkten (bps)",
    min_value=0.0,
    max_value=200.0,
    value=60.0,
    step=0.5,
    help="Standard sind 60 bps – du kannst hier einen anderen Wert eingeben."
)
if holdings_file and nav_file:
    try:
        holdings_excel = pd.ExcelFile(holdings_file)
        nav_excel = pd.ExcelFile(nav_file)

        holdings_sheet = holdings_excel.sheet_names[0]
        nav_sheet = nav_excel.sheet_names[0]

        holdings_df = holdings_excel.parse(holdings_sheet)
        nav_df = nav_excel.parse(nav_sheet)

        # NAV: Neueste Werte je ISIN
        latest_navs = nav_df.sort_values("month_end").drop_duplicates(subset="isin", keep="last")

        # Holdings aggregieren
        aggregated = holdings_df.groupby(["isin", "currency", "month_end"], as_index=False)["units"].sum()

        # Merge mit NAV
        merged = pd.merge(aggregated, latest_navs, on="isin", how="left")

        # Berechnung

        provision = holdings * bps_input / 10000 / 12

        merged["holding_value"] = merged["units"] * merged["nav"]
        merged["monthly_trail_fee"] = merged["holding_value"] * (bps / 10000) / 12

        # Umbenennen
        result = merged.rename(columns={
            "isin": "ISIN",
            "currency": "Currency",
            "units": "Units",
            "nav": "NAV",
            "holding_value": "Holding Value",
            "monthly_trail_fee": "Monthly Trail Fee",
            "month_end_x": "Holdings Date",
            "month_end_y": "NAV Date"
        })

        st.success("✅ Berechnung erfolgreich!")

        # Zeige Tabelle
        st.dataframe(result)

        # Download-Link
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            result.to_excel(writer, index=False, sheet_name="Provisionen")
        st.download_button("📥 Ergebnis als Excel herunterladen", data=output.getvalue(),
                           file_name="vertriebsprovisionen.xlsx", mime="application/vnd.ms-excel")

    except Exception as e:
        st.error(f"❌ Fehler bei der Verarbeitung: {e}")
else:
    st.info("Bitte lade beide Dateien hoch, um fortzufahren.")
