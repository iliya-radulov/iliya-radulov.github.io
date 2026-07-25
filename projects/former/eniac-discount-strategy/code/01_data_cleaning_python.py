import pandas as pd
import numpy as np

# =============================================================================
# PANDAS DATA CLEANING WORKFLOW
# =============================================================================


# -----------------------------------------------------------------------------
# STEP 1 & 2 — Read CSV and create DataFrame
# -----------------------------------------------------------------------------

df = pd.read_csv(
    "your_file.csv",
    # sep=",",            # delimiter (default: comma)
    # encoding="utf-8",   # encoding (default: utf-8)
    # parse_dates=["date_column"],  # parse date columns on load
    # na_values=["N/A", "n/a", ""],  # extra strings to treat as NaN
)


# -----------------------------------------------------------------------------
# STEP 3 — Inspect the DataFrame
# -----------------------------------------------------------------------------

print("--- Shape ---")
print(df.shape)                  # (rows, columns)

print("\n--- Column names ---")
print(df.columns.tolist())

print("\n--- Data types ---")
print(df.dtypes)

print("\n--- General info (non-null counts + dtypes) ---")
df.info()

print("\n--- First rows ---")
print(df.head())

print("\n--- Summary statistics ---")
print(df.describe(include="all"))


# -----------------------------------------------------------------------------
# STEP 4 — Check duplicates (count + percentage)
# -----------------------------------------------------------------------------

n_duplicates = df.duplicated().sum()
pct_duplicates = n_duplicates / len(df) * 100

print(f"\n--- Duplicates ---")
print(f"Count      : {n_duplicates}")
print(f"Percentage : {pct_duplicates:.2f}%")

# Preview duplicate rows
print(df[df.duplicated(keep=False)])


# -----------------------------------------------------------------------------
# STEP 5 — Drop or replace duplicates
# -----------------------------------------------------------------------------

# Option A — Drop all duplicates, keep first occurrence
df = df.drop_duplicates(keep="first")

# Option B — Drop duplicates based on specific columns only
# df = df.drop_duplicates(subset=["col1", "col2"], keep="first")

# Option C — Keep last occurrence
# df = df.drop_duplicates(keep="last")

print(f"\nShape after removing duplicates: {df.shape}")


# -----------------------------------------------------------------------------
# STEP 6 — Check missing / Null / NaN values
# -----------------------------------------------------------------------------

print("\n--- Missing values per column ---")
missing = df.isnull().sum()
missing_pct = df.isnull().mean() * 100

missing_report = pd.DataFrame({
    "missing_count": missing,
    "missing_%": missing_pct.round(2),
}).sort_values("missing_%", ascending=False)

print(missing_report[missing_report["missing_count"] > 0])


# -----------------------------------------------------------------------------
# STEP 7 — Drop or fill missing values
# -----------------------------------------------------------------------------

# --- Option A: Drop rows where ANY column is NaN ---
# df = df.dropna()

# --- Option B: Drop rows only if ALL columns are NaN ---
# df = df.dropna(how="all")

# --- Option C: Drop columns with more than X% missing ---
threshold = 0.5  # drop columns with >50% missing
df = df.dropna(thresh=int(len(df) * (1 - threshold)), axis=1)

# --- Option D: Fill with a fixed value ---
# df["column"] = df["column"].fillna(0)
# df["column"] = df["column"].fillna("Unknown")

# --- Option E: Fill with column mean / median ---
# df["numeric_col"] = df["numeric_col"].fillna(df["numeric_col"].mean())
# df["numeric_col"] = df["numeric_col"].fillna(df["numeric_col"].median())

# --- Option F: Forward fill / backward fill (time series) ---
# df["column"] = df["column"].ffill()
# df["column"] = df["column"].bfill()

print(f"\nShape after handling missing values: {df.shape}")
print(f"Remaining NaNs: {df.isnull().sum().sum()}")


# -----------------------------------------------------------------------------
# STEP 8 — Convert data types
# -----------------------------------------------------------------------------

# --- String / object ---
# df["col"] = df["col"].astype(str)
# df["col"] = df["col"].str.strip()        # remove leading/trailing whitespace
# df["col"] = df["col"].str.lower()        # normalise case

# --- Numeric ---
# df["col"] = df["col"].astype(int)
# df["col"] = df["col"].astype(float)
# df["col"] = pd.to_numeric(df["col"], errors="coerce")  # coerce: invalid → NaN

# --- Datetime ---
# df["date_col"] = pd.to_datetime(df["date_col"])
# df["date_col"] = pd.to_datetime(df["date_col"], format="%Y-%m-%d")
# df["date_col"] = pd.to_datetime(df["date_col"], dayfirst=True)  # for DD/MM/YYYY

# --- Categorical (saves memory for low-cardinality columns) ---
# df["cat_col"] = df["cat_col"].astype("category")

print("\n--- Final data types ---")
print(df.dtypes)


# -----------------------------------------------------------------------------
# DONE — Clean DataFrame ready
# -----------------------------------------------------------------------------

print("\n--- Final shape ---")
print(df.shape)

print("\n--- Remaining missing values ---")
print(df.isnull().sum())

# Optional: export cleaned data
# df.to_csv("cleaned_file.csv", index=False)
