
import os
import pandas as pd
import streamlit as st
import plotly.express as px


# PAGE CONFIGURATION

st.set_page_config(
    page_title="Customer Sentiment Dashboard",
    page_icon="📊",
    layout="wide"
)


# LOAD CLEANED DATA


st.title("📊 Customer Feedback & Sentiment Analysis")
st.caption(
    "Analyze customer opinions, product ratings, and review patterns."
)

if not os.path.exists("cleaned_reviews.csv"):
    st.error(
        "Cleaned dataset not found. Please run "
        "'python clean_data.py' in your terminal first."
    )
    st.stop()

df = pd.read_csv("cleaned_reviews.csv")

# Ensure required columns are available
df["Sentiment"] = df["Sentiment"].astype(str).str.strip().str.lower()
df["Rate_numeric"] = pd.to_numeric(
    df["Rate_numeric"], errors="coerce"
)

if "Review_Length" not in df.columns:
    df["Review_Length"] = df["Review"].astype(str).str.len()

# ==========================================
# SIDEBAR FILTERS
# ==========================================

st.sidebar.title("Dashboard Filters")
st.sidebar.caption("Customize the data shown below.")

sentiment_options = [
    s for s in ["positive", "neutral", "negative"]
    if s in df["Sentiment"].unique()
]

selected_sentiments = st.sidebar.multiselect(
    "Select sentiment",
    options=sentiment_options,
    default=sentiment_options
)

rating_options = sorted(
    df["Rate_numeric"].dropna().unique().tolist()
)

selected_ratings = st.sidebar.multiselect(
    "Select star ratings",
    options=rating_options,
    default=rating_options,
    format_func=lambda x: f"{x:g} stars"
)

# Apply filters
filtered_df = df[
    df["Sentiment"].isin(selected_sentiments)
    & df["Rate_numeric"].isin(selected_ratings)
].copy()

st.sidebar.divider()
st.sidebar.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} reviews."
)

# KPI SUMMARY CARDS

st.subheader("Business Overview")

total_reviews = len(filtered_df)

positive_percentage = (
    (filtered_df["Sentiment"] == "positive").mean() * 100
    if total_reviews else 0
)

average_rating = filtered_df["Rate_numeric"].mean()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Reviews",
    f"{total_reviews:,}"
)

col2.metric(
    "Positive Reviews",
    f"{positive_percentage:.1f}%"
)

col3.metric(
    "Average Star Rating",
    f"{average_rating:.2f} / 5"
    if pd.notna(average_rating) else "N/A"
)

st.divider()

if filtered_df.empty:
    st.warning("No reviews match your selected filters.")
    st.stop()


# CHART 1: SENTIMENT DISTRIBUTION


st.subheader("1. Customer Sentiment Distribution")
st.caption(
    "Understand whether customer feedback is positive, neutral, or negative."
)

sentiment_counts = (
    filtered_df["Sentiment"]
    .value_counts()
    .reindex(["positive", "neutral", "negative"], fill_value=0)
    .reset_index()
)

sentiment_counts.columns = ["Sentiment", "Reviews"]

sentiment_colors = {
    "positive": "#10B981",
    "neutral": "#F59E0B",
    "negative": "#EF4444"
}

fig1 = px.pie(
    sentiment_counts,
    names="Sentiment",
    values="Reviews",
    hole=0.55,
    color="Sentiment",
    color_discrete_map=sentiment_colors
)

fig1.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

fig1.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    legend_title_text="Sentiment"
)

st.plotly_chart(fig1, use_container_width=True)

# ==========================================
# CHART 2: RATING DISTRIBUTION
# ==========================================

st.subheader("2. Customer Rating Distribution")
st.caption(
    "See how many customers gave each star rating."
)

rating_counts = (
    filtered_df["Rate_numeric"]
    .dropna()
    .value_counts()
    .sort_index()
    .rename_axis("Rating")
    .reset_index(name="Reviews")
)

fig2 = px.bar(
    rating_counts,
    x="Rating",
    y="Reviews",
    text="Reviews",
    color="Rating",
    color_continuous_scale="Blues"
)

fig2.update_layout(
    xaxis_title="Star Rating",
    yaxis_title="Number of Reviews",
    coloraxis_showscale=False,
    margin=dict(t=20, b=20)
)

fig2.update_xaxes(dtick=1)

st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# CHART 3: RATING VS SENTIMENT
# ==========================================

st.subheader("3. Relationship Between Rating and Sentiment")
st.caption(
    "Compare customer star ratings with the sentiment labels in the dataset."
)

rating_sentiment = (
    filtered_df.dropna(subset=["Rate_numeric"])
    .groupby(["Rate_numeric", "Sentiment"])
    .size()
    .reset_index(name="Reviews")
)

fig3 = px.bar(
    rating_sentiment,
    x="Rate_numeric",
    y="Reviews",
    color="Sentiment",
    barmode="stack",
    category_orders={
        "Sentiment": ["negative", "neutral", "positive"]
    },
    color_discrete_map=sentiment_colors,
    labels={
        "Rate_numeric": "Star Rating",
        "Reviews": "Number of Reviews"
    }
)

fig3.update_layout(
    margin=dict(t=20, b=20),
    legend_title_text="Sentiment"
)

fig3.update_xaxes(dtick=1)

st.plotly_chart(fig3, use_container_width=True)

# ==========================================
# CHART 4: AVERAGE REVIEW LENGTH
# ==========================================

st.subheader("4. Average Review Length by Sentiment")
st.caption(
    "Compare the average number of characters in reviews across sentiment groups."
)

length_data = (
    filtered_df.groupby("Sentiment")["Review_Length"]
    .mean()
    .reindex(["positive", "neutral", "negative"])
    .dropna()
    .rename("Average Characters")
    .reset_index()
)

fig4 = px.bar(
    length_data,
    x="Sentiment",
    y="Average Characters",
    color="Sentiment",
    color_discrete_map=sentiment_colors,
    text_auto=".1f"
)

fig4.update_layout(
    showlegend=False,
    margin=dict(t=20, b=20),
    yaxis_title="Average Characters"
)

st.plotly_chart(fig4, use_container_width=True)

# ==========================================
# ADDITIONAL BUSINESS INSIGHTS
# ==========================================

st.divider()
st.subheader("💡 Key Business Insights")

insight1, insight2 = st.columns(2)

with insight1:
    st.markdown("**Most Common Sentiment**")

    common_sentiment = filtered_df["Sentiment"].mode()

    if not common_sentiment.empty:
        sentiment_name = common_sentiment.iloc[0].title()
        sentiment_share = (
            filtered_df["Sentiment"].eq(
                common_sentiment.iloc[0]
            ).mean() * 100
        )

        st.markdown(f"### {sentiment_name}")
        st.write(
            f"{sentiment_share:.1f}% of the filtered reviews "
            f"are labelled {sentiment_name.lower()}."
        )

with insight2:
    st.markdown("**Most-Reviewed Product**")

    if "product_name" in filtered_df.columns:
        product_counts = (
            filtered_df["product_name"]
            .dropna()
            .value_counts()
        )

        if not product_counts.empty:
            top_product = product_counts.index[0]
            top_product_count = product_counts.iloc[0]

            st.markdown(
                f"### {top_product}",
                help="Product with the highest number of reviews in the filtered data."
            )
            st.write(
                f"{top_product_count:,} reviews in the filtered dataset."
            )
        else:
            st.info("Product names are unavailable.")
    else:
        st.info("Product names are unavailable.")

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Customer Feedback & Sentiment Analysis | "
    "Built with Python, Pandas, Plotly and Streamlit"
)
