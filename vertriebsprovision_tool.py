
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Vertriebsprovisionen", layout="wide")
st.title("📊 Vertriebsprovisionen mit variablen Basispunkten pro ISIN")

# Datei-Uploads
st.header("1. 📥 Dateien hochladen")
holdings_file = st.file_uploader("Holdings-Datei (Excel)", type=["xlsx"])
nav_file = st.file_uploader("NAV-Datei (Excel)", type=["xlsx"])
bps_file = st.file_uploader("Bps pro ISIN (Excel)", type=["xlsx"])

if holdings_file and nav_file and bps_file:
    try:
        # Einlesen der Dateien
        holdings_df = pd.read_excel(holdings_file)
        nav_df = pd.read_excel(nav_file)
        bps_df = pd.read_excel(bps_file)

        # Erwartete Spalten prüfen
        expected_holdings_cols = {"isin", "fund_name", "units", "currency", "month_end"}
        expected_nav_cols = {"isin", "nav", "month_end"}
        expected_bps_cols = {"isin", "bps"}

        if not expected_holdings_cols.issubset(holdings_df.columns):
            st.error(f"❌ Holdings-Datei muss diese Spalten enthalten: {expected_holdings_cols}")
        elif not expected_nav_cols.issubset(nav_df.columns):
            st.error(f"❌ NAV-Datei muss diese Spalten enthalten: {expected_nav_cols}")
        elif not expected_bps_cols.issubset(bps_df.columns):
            st.error(f"❌ Bps-Datei muss diese Spalten enthalten: {expected_bps_cols}")
        else:
            # Merge NAV zu Holdings
            merged = holdings_df.merge(nav_df, on=["isin", "month_end"], how="left")
            # Merge BPS pro ISIN
            merged = merged.merge(bps_df, on="isin", how="left")

            # Berechnung der Holdings
            merged["holdings"] = merged["units"] * merged["nav"]

            # Berechnung der Provision
            merged["provision"] = merged["holdings"] * merged["bps"] / 10000 / 12

            st.success("✅ Berechnung erfolgreich!")
            st.dataframe(merged[["isin", "fund_name", "units", "nav", "bps", "holdings", "provision", "currency", "month_end"]])

            # Download-Datei
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                merged.to_excel(writer, index=False, sheet_name="Vertriebsprovision")
            st.download_button("📥 Ergebnisse herunterladen", data=output.getvalue(), file_name="vertriebsprovisionen.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"Fehler bei der Verarbeitung: {e}")
else:
    st.info("⬆️ Bitte lade alle drei Dateien hoch, um die Berechnung zu starten.")
