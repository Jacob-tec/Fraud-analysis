import pandas as pd
import streamlit as st
import plotly.express as px
import os  # Import the os module to handle file paths

# --- Configuration ---
st.set_page_config(page_title="Credit Card Transactions Dashboard", layout="wide")

st.title("💳 Credit Card Transactions Dashboard")


# --- Data Loading ---
# The @st.cache_data decorator caches the DataFrame so it's loaded only once,
# which is crucial for performance in Streamlit apps.
@st.cache_data
def load_data(file_path):
    """
    Loads the credit card transaction data from a CSV file.
    Includes error handling for FileNotFoundError.
    """
    try:
        df = pd.read_csv(file_path)
        # Ensure 'hour', 'amt', 'category', 'weekday' columns exist for filtering and plotting
        required_columns = ['hour', 'amt', 'category', 'weekday']
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Error: Required column '{col}' not found in the CSV file.")
                st.stop()  # Stop the app if a critical column is missing

        # Ensure numeric columns are of correct type, coercing errors
        df['amt'] = pd.to_numeric(df['amt'], errors='coerce')
        df['hour'] = pd.to_numeric(df['hour'], errors='coerce').astype('Int64')  # Use Int64 to allow NaN

        # Drop rows where critical numeric data (amount or hour) is missing after coercion
        initial_rows = len(df)
        df.dropna(subset=['amt', 'hour'], inplace=True)
        if len(df) < initial_rows:
            st.warning(f"Removed {initial_rows - len(df)} rows due to missing or invalid 'amt' or 'hour' values.")

        # If 'is_fraud' exists, ensure it's a boolean or suitable for categorical plotting
        if 'is_fraud' in df.columns:
            # Convert 'is_fraud' to boolean or category if it's 0/1, for clear plotting
            df['is_fraud'] = df['is_fraud'].astype(bool)  # Or .astype('category')

        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found.")
        st.markdown("""
        **Please ensure your project structure matches the following:**
        ```
        credit-card-analysis/
        ├── app/
        │   └── dashboard.py  <- This script
        └── data/
            └── cleansed/
                └── fraudTest_clean.csv <- Your data file
        ```
        If your file is in a different location, you might need to adjust the `file_path`
        variable in the `load_data` function.
        """)
        st.stop()  # Stop the app execution if file is not found
    except pd.errors.EmptyDataError:
        st.error(f"Error: The file '{file_path}' is empty.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred while loading or processing data: {e}")
        st.stop()


# Define the relative path to your data file
# This path assumes 'dashboard.py' is inside an 'app' folder,
# and the 'data' folder is one level up.
file_path_to_csv = "data/cleansed/FraudTest_clean.csv"

# Load the data using the cached function
df = load_data(file_path_to_csv)

# --- Filters ---
st.sidebar.header("Filters")

# Using the actual min/max values from the loaded DataFrame for sliders
min_hour = df['hour'].min() if not df['hour'].isnull().all() else 0
max_hour = df['hour'].max() if not df['hour'].isnull().all() else 23

time_range = st.sidebar.slider(
    "Hour Range",
    min_value=int(min_hour),
    max_value=int(max_hour),
    value=(int(min_hour), int(max_hour))
)

min_amt = float(df['amt'].min()) if not df['amt'].isnull().all() else 0.0
max_amt = float(df['amt'].max()) if not df['amt'].isnull().all() else 1000.0

amount_range = st.sidebar.slider(
    "Transaction Amount Range",
    min_value=min_amt,
    max_value=max_amt,
    value=(min_amt, max_amt)
)

# Get unique categories and sort them for better presentation
unique_categories = sorted(df['category'].unique().tolist())
merchant_category = st.sidebar.multiselect(
    "Merchant Category",
    options=unique_categories,
    default=unique_categories  # Default to selecting all categories
)

# --- Filter Data ---
# Apply filters only if the data frame is not empty after initial load and cleaning
if not df.empty:
    df_filtered = df[
        (df['hour'] >= time_range[0]) &
        (df['hour'] <= time_range[1]) &
        (df['amt'] >= amount_range[0]) &
        (df['amt'] <= amount_range[1]) &
        (df['category'].isin(merchant_category))
        ].copy()  # Use .copy() to avoid SettingWithCopyWarning
else:
    df_filtered = pd.DataFrame()  # Create an empty DataFrame if initial load failed or was empty
    st.warning("No data available to display visualizations. Please check your data file.")

# --- Visualizations ---
# Only attempt to create plots if the filtered DataFrame is not empty
if not df_filtered.empty:
    st.subheader("Transaction Amount Distribution")
    fig_hist = px.histogram(df_filtered, x="amt", nbins=50, title="Transaction Amount Distribution")
    st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("Transactions by Hour and Weekday")
    # Group by hour and weekday, then unstack for heatmap if preferred, or use density_heatmap
    # Ensure 'weekday' is categorical for correct sorting on y-axis
    # Assuming 'weekday' column exists and is already properly formatted (e.g., 0-6 for Mon-Sun or string names)
    # If 'weekday' is not already a string representing names, you might want to map it:
    # df_filtered['weekday_name'] = df_filtered['weekday'].map({0: 'Mon', 1: 'Tue', ...})

    # For robust plotting, let's ensure 'weekday' is treated as an ordered categorical
    # if it's numerical (e.g., 0-6), or if it's strings like Mon, Tue.
    # If 'weekday' is numerical (0-6), you might want to convert it to actual weekday names for better labels
    # Example mapping (adjust if your weekday numbers start from a different day):
    # weekday_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    # df_filtered['weekday_name'] = df_filtered['weekday'].map(weekday_map)

    # Using existing 'weekday' assuming it's suitable for direct plotting or will be properly ordered by plotly
    heatmap_data = df_filtered.groupby(['hour', 'weekday']).size().reset_index(name='count')

    fig_heatmap = px.density_heatmap(
        heatmap_data,
        x='hour',
        y='weekday',
        z='count',
        color_continuous_scale='Viridis',
        title="Transaction Volume by Hour & Weekday"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Conditional visualization for 'is_fraud'
    if 'is_fraud' in df.columns and not df_filtered['is_fraud'].isnull().all():
        st.subheader("Fraud vs Non-Fraud Amounts")
        fig_box = px.box(df_filtered, x='is_fraud', y='amt', points="all", title="Fraud vs Non-Fraud Amounts")
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info(
            "The 'is_fraud' column is not available or contains no valid data in the filtered dataset for the 'Fraud vs Non-Fraud Amounts' visualization.")

else:
    st.warning("No data matches the current filter selections. Please adjust your filters.")

