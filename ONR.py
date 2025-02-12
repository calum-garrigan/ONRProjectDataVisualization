# ✅ Install required packages before running:
# pip install streamlit plotly pandas numpy

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random

# 🎯 Generate a large dataset with variety
schools = ["IMC", "BIM"]
year_classes = [f"24-{i}" for i in range(1, 13)]
test_levels = ["TT2H100", "TT2H200", "TT2H300"]

large_data = {
    "School": [random.choice(schools) for _ in range(200)],
    "Year_Class": [random.choice(year_classes) for _ in range(200)],
    "Test Level": [random.choice(test_levels) for _ in range(200)],
    "TTP": [round(random.uniform(5, 12), 2) for _ in range(200)],
    "TTT": [round(random.uniform(8, 15), 2) for _ in range(200)],
    "S/A": [round(random.uniform(4, 9), 2) for _ in range(200)]
}

df_large = pd.DataFrame(large_data)

# Add a logo above the title
st.image("ONR LOGO.png", width=200)  # Adjust width as needed

# 🔹 Sidebar Filters
selected_school = st.sidebar.selectbox("Select School", ["All"] + sorted(df_large["School"].unique()))
selected_class = st.sidebar.selectbox("Select Year Class", ["All"] + sorted(df_large["Year_Class"].unique()))

# 📌 Apply filters
filtered_df = df_large.copy()
if selected_school != "All":
    filtered_df = filtered_df[filtered_df["School"] == selected_school]
if selected_class != "All":
    filtered_df = filtered_df[filtered_df["Year_Class"] == selected_class]

# 📌 Check if data is available
if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters.")
else:
    test_levels = filtered_df["Test Level"].unique()
    ttp = filtered_df.groupby("Test Level")["TTP"].mean().reindex(test_levels, fill_value=0)
    ttt = filtered_df.groupby("Test Level")["TTT"].mean().reindex(test_levels, fill_value=0)
    sa = filtered_df.groupby("Test Level")["S/A"].mean().reindex(test_levels, fill_value=0)

    # 📊 Create one interactive stacked bar chart
    fig = go.Figure()

    # Adjust bar heights so some bars reach the top dotted line
    scale_factor = max(ttp + ttt + sa) / max(sa)  
    sa = sa * scale_factor * 0.9  

    for i, level in enumerate(test_levels):
        if i == 0:
            # **First stacked bar → TTP (bottom), S/A (top) (NO TTT)**
            fig.add_trace(go.Bar(x=[level], y=[ttp[level]], name='TTP (Time to Process)', 
                             marker_color='blue', legendgroup="TTP", showlegend=True))
            fig.add_trace(go.Bar(x=[level], y=[sa[level]], name='S/A (Split Accuracy)', 
                             marker_color='gray', legendgroup="S/A", showlegend=True))
        else:
            # **All other bars → TTT (bottom), S/A (top) (NO TTP)**
            fig.add_trace(go.Bar(x=[level], y=[ttt[level]], name='TTT (Total Task Time)', 
                             marker_color='green', legendgroup="TTT", showlegend=(i == 1)))
            fig.add_trace(go.Bar(x=[level], y=[sa[level]], name='S/A (Split Accuracy)', 
                             marker_color='gray', legendgroup="S/A", showlegend=False))

    # 📌 Add horizontal dotted lines (Thicker) with hover buttons only
    y_max = max(ttp + ttt + sa)
    percentiles = [y_max * 0.75, y_max * 0.50, y_max * 0.25]

    labels = {
        "75%": "75% (Percentile)<br>Speed: Slow – Shooter takes longer than 75% of competitors.<br>"
               "Accuracy: High – Shooter is more accurate than 75% of competitors.<br>"
               "Overall: If this relates to speed, it's bad (too slow). If it relates to accuracy, it's good (high precision).",

        "50%": "50% (Percentile)<br>Speed: Average – Shooter performs at the median level.<br>"
               "Accuracy: Moderate – About as accurate as the middle of the group.<br>"
               "Overall: Neutral—not outstanding but not poor.",

        "25%": "25% (Percentile)<br>Speed: Fast – Shooter is quicker than 75% of competitors.<br>"
               "Accuracy: Low – Shooter is less accurate than 75% of competitors.<br>"
               "Overall: If this relates to speed, it’s good (faster than most). If it relates to accuracy, it’s bad (less precise)."
    }

    for y, label_key in zip(percentiles, labels.keys()):
        # Dotted horizontal line
        fig.add_trace(go.Scatter(
            x=[test_levels[0], test_levels[-1]], y=[y, y], mode="lines",
            line=dict(dash='dot', width=2.5, color="black"),  # Thicker dotted lines
            hoverinfo="none",
            showlegend=False
        ))

        # Hover button (no text on graph, only hover)
        fig.add_trace(go.Scatter(
            x=[test_levels[-1]], y=[y], mode="markers",
            marker=dict(color="black", size=10),
            hoverinfo="text",
            text=[labels[label_key]],  # Shows text only when hovered
            showlegend=False  # Keeps legend clean
        ))

    # 🎨 Layout settings (Bigger Graph)
    fig.update_layout(
        barmode='stack',
        title=f"📊 Stacked Metrics by Test Level (School: {selected_school}, Class: {selected_class})",
        xaxis_title="Test Level",
        yaxis_title="Percentile",
        xaxis=dict(tickangle=-45),
        yaxis=dict(
            tickmode="array",
            tickvals=percentiles,
            ticktext=["75%", "50%", "25%"]
        ),
        hovermode="closest",  # Ensures hover works properly
        height=700,  # Bigger graph height
        width=1000,  # Bigger graph width
        showlegend=True  # ✅ Keeps only test labels in the legend
    )

    # 📊 Show chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
