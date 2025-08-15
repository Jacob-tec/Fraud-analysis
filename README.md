# Fraud-analysis
Credit Card Fraud Detection Dashboard

An interactive Streamlit + Plotly dashboard for exploring, filtering, and analyzing credit card transaction datasets. This project includes data cleaning workflows, fraud analysis visualizations, and a fully interactive dashboard for detecting suspicious patterns in transactions.

📥 Downloading the Data

The dataset used in this project is Fraud Detection Dataset from Kaggle.
Since the dataset is too large to host on GitHub, you need to download it manually:

    Create a free Kaggle account.

    Go to the dataset page: Fraud Detection Dataset.

    Click Download and extract the contents.

    Place the file fraudTest.csv into:

    data/raw/

🧹 Cleaning the Data

    Open the notebooks/data_cleaning.ipynb in Jupyter Notebook or Jupyter Lab.

    Run all cells — this will:

        Remove duplicates and null values

        Format columns (dates, transaction amounts)

        Save the cleaned dataset as:

        data/cleansed/FraudTest_clean.csv

    This cleaned file will be used by the dashboard.

🚀 Running the Dashboard

    Install dependencies:

pip install -r requirements.txt

Run the Streamlit app from the app/ folder:

    cd app
    streamlit run dashboard.py

    Open the provided local URL in your browser.

📊 Features

    Interactive Filtering by time of day, transaction amount, and merchant category.

    Dynamic Charts for fraud amount distributions, merchant categories, and transaction timing.

    Easy Data Pipeline with reproducible cleaning and EDA notebooks.

🛠 Tech Stack

    Python: Pandas, NumPy

    Visualization: Plotly Express

    Dashboard: Streamlit

    Notebooks: Jupyter
