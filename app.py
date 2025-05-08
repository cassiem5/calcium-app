import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("Calcium Imaging Processor")

# ---- Helper Functions ----
def parse_pasted_data(pasted_text):
    try:
        rows = [row.strip().split() for row in pasted_text.strip().split('\n') if row.strip()]
        df = pd.DataFrame(rows).apply(pd.to_numeric, errors='coerce')
        return df.dropna(how='all', axis=1)
    except Exception as e:
        st.error(f"Failed to parse data: {e}")
        return None

def process_field_data(baseline_text, data_text):
    if not baseline_text.strip() or not data_text.strip():
        return None

    baseline_df = parse_pasted_data(baseline_text)
    data_df = parse_pasted_data(data_text)

    if baseline_df is None or data_df is None:
        return None

    baseline_values = baseline_df.iloc[0, 1:].values
    time_col = data_df.iloc[:, 0]
    value_cols = data_df.iloc[:, 1:]

    max_values = value_cols.max().values
    delta = max_values - baseline_values
    half_delta = delta / 2
    t50_value = max_values - half_delta

    max_times = []
    t50_times = []
    t50_durations = []

    for col_idx in range(value_cols.shape[1]):
        max_idx = value_cols.iloc[:, col_idx].idxmax()
        max_time = time_col.iloc[max_idx]
        max_times.append(max_time)

        after_max = value_cols.iloc[max_idx:, col_idx]
        below_t50 = after_max[after_max <= t50_value[col_idx]]

        if not below_t50.empty:
            t50_idx = below_t50.index[0]
            t50_time = time_col.iloc[t50_idx]
            t50_times.append(t50_time)
            t50_durations.append(round(t50_time - max_time, 7))
        else:
            t50_times.append(np.nan)
            t50_durations.append(np.nan)

    return pd.DataFrame({
        "Baseline": baseline_values,
        "Max": max_values,
        "Delta": delta,
        "1/2 Delta": half_delta,
        "T50 Value": t50_value,
        "Max Time": max_times,
        "T50 Time": t50_times,
        "T50": t50_durations
    })

# ---- UI Layout ----
tabs = st.tabs([f"Coverslip {i}" for i in range(1, 5)])

for tab in tabs:
    with tab:
        for row_num in range(1, 5):
            st.markdown(f"### Field {row_num}")
            col1, col2 = st.columns(2)

            with col1:
                baseline_text = st.text_area(f"Paste Baseline Data (times & values) - Field {row_num}", key=f"baseline_{tab}_{row_num}")
            with col2:
                data_text = st.text_area(f"Paste Data (times & values) - Field {row_num}", key=f"data_{tab}_{row_num}")

            if st.button(f"Process Field {row_num}", key=f"process_{tab}_{row_num}"):
                df = process_field_data(baseline_text, data_text)
                if df is not None:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Invalid or missing input for this field.")

st.markdown("---")
st.caption("Built with ❤️ for calcium imaging analysis")
