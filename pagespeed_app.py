import streamlit as st
import requests
import pandas as pd
import time
import io

# ======================
# CONFIGURATION
# ======================
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your Google PageSpeed API key

# ======================
# FUNCTION TO TEST A URL
# ======================
def test_url(url, device):
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "strategy": device,
        "key": API_KEY
    }

    try:
        response = requests.get(endpoint, params=params)
        data = response.json()

        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        audits = lighthouse.get("audits", {})

        perf_score = categories.get("performance", {}).get("score", None)
        if perf_score is not None:
            perf_score = round(perf_score * 100)  # Convert to 0–100 %

        fcp = audits.get("first-contentful-paint", {}).get("displayValue", "")
        lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "")
        tbt = audits.get("total-blocking-time", {}).get("displayValue", "")
        cls = audits.get("cumulative-layout-shift", {}).get("displayValue", "")

        return {
            "URL": url,
            "Device": device,
            "Performance Score": perf_score,
            "FCP": fcp,
            "LCP": lcp,
            "TBT": tbt,
            "CLS": cls
        }

    except Exception as e:
        return {
            "URL": url,
            "Device": device,
            "Performance Score": "Error",
            "FCP": str(e),
            "LCP": "",
            "TBT": "",
            "CLS": ""
        }

# ======================
# STREAMLIT APP
# ======================
st.title("Bulk Website Speed Tester (Google PageSpeed API)")

uploaded_file = st.file_uploader("Upload a .txt file with URLs (one per line)", type=["txt"])

if uploaded_file is not None:
    urls = uploaded_file.read().decode("utf-8").splitlines()
    urls = list(dict.fromkeys([u.strip() for u in urls if u.strip()]))  # remove duplicates & blanks

    st.write(f"✅ {len(urls)} unique URLs loaded")

    if st.button("Run Test"):
        results = []
        progress_bar = st.progress(0)

        for i, url in enumerate(urls):
            for device in ["mobile", "desktop"]:
                result = test_url(url, device)
                results.append(result)
                time.sleep(1)  # avoid hitting API rate limits

            progress_bar.progress((i + 1) / len(urls))

        df = pd.DataFrame(results)
        st.subheader("Results")
        st.dataframe(df)

        # Export CSV
        output = io.StringIO()
        df.to_csv(output, index=False)
        csv_data = output.getvalue()

        st.download_button(
            label="Download Results as CSV",
            data=csv_data,
            file_name="pagespeed_results.csv",
            mime="text/csv"
        )
