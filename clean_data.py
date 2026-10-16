
import pandas as pd

# ==========================================
# STEP 1: LOAD THE ORIGINAL DATASET
# ==========================================

df = pd.read_csv("Dataset-SA.csv")

print("--- ORIGINAL DATASET ---")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ==========================================
# STEP 2: CHECK DATA QUALITY
# ==========================================

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DUPLICATE ROWS ---")
print("Exact duplicates:", df.duplicated().sum())

print("\n--- ORIGINAL SENTIMENT DISTRIBUTION ---")
print(df["Sentiment"].value_counts(dropna=False))

print("\n--- INVALID RATINGS ---")

# Convert ratings into numeric values.
# Invalid values will become NaN.
df["Rate_numeric"] = pd.to_numeric(
    df["Rate"], errors="coerce"
)

print("Invalid ratings:", df["Rate_numeric"].isna().sum())


# ==========================================
# STEP 3: CREATE A CLEANED COPY
# ==========================================

clean_df = df.copy()

# Remove unnecessary spaces from text columns.
for column in ["Review", "Summary", "Sentiment"]:
    clean_df[column] = clean_df[column].astype("string").str.strip()

# Standardize sentiment labels.
clean_df["Sentiment"] = clean_df["Sentiment"].str.lower()

# Convert blank strings into missing values.
clean_df["Review"] = clean_df["Review"].replace("", pd.NA)
clean_df["Summary"] = clean_df["Summary"].replace("", pd.NA)
clean_df["Sentiment"] = clean_df["Sentiment"].replace("", pd.NA)

# Remove rows without review text or sentiment labels.
before_missing_removal = len(clean_df)

clean_df = clean_df.dropna(
    subset=["Review", "Sentiment"]
).copy()

removed_missing = before_missing_removal - len(clean_df)


# ==========================================
# STEP 4: CLEAN AND VALIDATE RATINGS
# ==========================================

# Create a numeric rating column.
clean_df["Rate_numeric"] = pd.to_numeric(
    clean_df["Rate"], errors="coerce"
)

# Keep only valid star ratings from 1 to 5.
# Rows with invalid ratings are retained because
# their review text may still be useful.
invalid_rating_count = (
    clean_df["Rate_numeric"].isna()
    | ~clean_df["Rate_numeric"].between(1, 5)
).sum()

print("\n--- RATING CHECK ---")
print("Rows with missing or invalid ratings:", invalid_rating_count)


# ==========================================
# STEP 5: STANDARDIZE SENTIMENT LABELS
# ==========================================

# Keep only the expected sentiment categories.
valid_sentiments = ["positive", "neutral", "negative"]

before_sentiment_check = len(clean_df)

clean_df = clean_df[
    clean_df["Sentiment"].isin(valid_sentiments)
].copy()

removed_invalid_sentiments = (
    before_sentiment_check - len(clean_df)
)


# ==========================================
# STEP 6: REMOVE EXACT DUPLICATES
# ==========================================

before_duplicates = len(clean_df)

clean_df = clean_df.drop_duplicates().copy()

removed_duplicates = before_duplicates - len(clean_df)


# ==========================================
# STEP 7: ADD USEFUL ANALYSIS COLUMNS
# ==========================================

# Review length measured in characters.
clean_df["Review_Length"] = clean_df["Review"].str.len()

# Numeric rating is retained for charts and analysis.
# The original Rate column is also preserved.


# ==========================================
# STEP 8: SAVE THE CLEANED DATASET
# ==========================================

clean_df.to_csv("cleaned_reviews.csv", index=False)


# ==========================================
# STEP 9: DISPLAY CLEANING SUMMARY
# ==========================================

print("\n--- CLEANING SUMMARY ---")

print("Original rows:", len(df))
print("Rows removed due to missing review/sentiment:", removed_missing)
print("Rows removed due to invalid sentiment labels:", removed_invalid_sentiments)
print("Exact duplicate rows removed:", removed_duplicates)
print("Rows with invalid ratings retained:", invalid_rating_count)
print("Final cleaned rows:", len(clean_df))
print("Final columns:", len(clean_df.columns))

print("\n--- CLEANED SENTIMENT DISTRIBUTION ---")
print(clean_df["Sentiment"].value_counts())

print("\nCleaned dataset saved as cleaned_reviews.csv")
