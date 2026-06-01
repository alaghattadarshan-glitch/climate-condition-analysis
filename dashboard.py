import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Climate Condition Analysis Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (injecting premium CSS styles)
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.15rem;
        color: #64748B;
        margin-bottom: 1.8rem;
    }
    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1E293B;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 0.4rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stAlert {
        border-radius: 0.75rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    div[data-testid="metric-container"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 0.75rem;
        padding: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Import backend modules from climate_analysis
try:
    from climate_analysis import (
        generate_sample_data,
        load_and_preprocess_data,
        perform_climate_analysis,
        generate_insights
    )
except ImportError:
    st.error("Could not import functions from `climate_analysis.py`. Make sure the script is in the same directory.")
    st.stop()

# Helper to verify data files
DATASET_FILE = "climate_data.csv"
if not os.path.exists(DATASET_FILE):
    st.warning("Climate dataset not found. Generating sample data...")
    generate_sample_data(DATASET_FILE)

# Load data (cached for performance)
@st.cache_data
def get_clean_data(filepath):
    df_clean, summary_stats = load_and_preprocess_data(filepath)
    results = perform_climate_analysis(df_clean)
    insights = generate_insights(df_clean, results)
    return df_clean, summary_stats, results, insights

# Load data
df, summary_stats, results, insights = get_clean_data(DATASET_FILE)

# ==============================================================================
# SIDEBAR - Navigation, Filtering & Dynamic Modifiers
# ==============================================================================
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=300&q=80", use_container_width=True)
    st.title("Climate Analytics Hub")
    
    # 1. Page Selector
    page = st.radio(
        "Select Dashboard Section",
        [
            "📊 Overview & Dataset",
            "📈 Statistical Analysis",
            "🎨 Visualizations Dashboard"
        ]
    )
    
    st.markdown("---")
    st.subheader("Global Data Filters")
    
    # 2. Year Filter
    years = sorted(df["Year"].unique())
    selected_years = st.multiselect("Select Years", years, default=years)
    
    # 3. Weather Condition Filter
    conditions = df["Weather Condition"].unique()
    selected_conditions = st.multiselect("Select Weather Conditions", conditions, default=conditions)

    st.markdown("---")
    st.subheader("Dynamic View Modifiers")
    
    # 4. Dynamic Column Remover (allows removing columns in real-time)
    removable_columns = ["Temperature (°C)", "Humidity (%)", "Rainfall (mm)", "Wind Speed (km/h)", "Atmospheric Pressure (hPa)", "Weather Condition"]
    columns_to_remove = st.multiselect(
        "Remove Columns dynamically",
        removable_columns,
        default=[]
    )
    
    # 5. Dynamic Rolling average slider (floating window size for smoothing lines)
    rolling_window = st.slider(
        "Line Smoothing window (Days)",
        min_value=5,
        max_value=90,
        value=30,
        step=5
    )

# Apply filters
filtered_df = df[
    (df["Year"].isin(selected_years)) & 
    (df["Weather Condition"].isin(selected_conditions))
]

# Apply Dynamic Column Removal
active_columns = [col for col in filtered_df.columns if col not in columns_to_remove]
filtered_df = filtered_df[active_columns]

# Ensure there is data after filtering
if filtered_df.empty:
    st.warning("No data found matching current filters. Please expand your selection in the sidebar.")
    st.stop()

# Define Color Palette for Weather Conditions (Plotly discrete maps)
colors_map = {
    "Sunny": "#F59E0B",    # Amber/Yellow
    "Cloudy": "#64748B",   # Slate Grey
    "Rainy": "#3B82F6",    # Blue
    "Stormy": "#6366F1"    # Indigo
}

# ==============================================================================
# PAGE 1: Overview & Dataset
# ==============================================================================
if page == "📊 Overview & Dataset":
    st.markdown('<div class="main-title">Climate Condition Analysis Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">An advanced interactive web application demonstrating climate physics and statistical trends</div>', unsafe_allow_html=True)
    
    # Key Performance Indicators (KPIs) - only render if the column exists
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        if "Temperature (°C)" in filtered_df.columns:
            st.metric(
                label="🌡️ Average Temperature",
                value=f"{filtered_df['Temperature (°C)'].mean():.2f} °C",
                delta=f"{filtered_df['Temperature (°C)'].max() - filtered_df['Temperature (°C)'].min():.1f} °C Range"
            )
        else:
            st.info("🌡️ Temperature column removed.")
            
    with kpi2:
        if "Humidity (%)" in filtered_df.columns:
            st.metric(
                label="💧 Average Humidity",
                value=f"{filtered_df['Humidity (%)'].mean():.1f} %",
                delta=f"± {filtered_df['Humidity (%)'].std():.1f} % StdDev"
            )
        else:
            st.info("💧 Humidity column removed.")
            
    with kpi3:
        if "Wind Speed (km/h)" in filtered_df.columns:
            st.metric(
                label="💨 Average Wind Speed",
                value=f"{filtered_df['Wind Speed (km/h)'].mean():.2f} km/h",
                delta=f"{filtered_df['Wind Speed (km/h)'].max():.1f} km/h Max"
            )
        else:
            st.info("💨 Wind Speed column removed.")
            
    with kpi4:
        if "Rainfall (mm)" in filtered_df.columns:
            st.metric(
                label="🌧️ Total Rainfall",
                value=f"{filtered_df['Rainfall (mm)'].sum():.1f} mm",
                delta=f"Avg {filtered_df['Rainfall (mm)'].mean():.2f} mm/day"
            )
        else:
            st.info("🌧️ Rainfall column removed.")
        
    st.markdown('<div class="section-header">📋 Climate Dataset Explorer</div>', unsafe_allow_html=True)
    st.write(f"Displaying **{len(filtered_df)}** records matching active filters. Active columns: `{list(filtered_df.columns)}`")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    # File Download Link
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Cleaned Dataset (CSV)",
        data=csv,
        file_name="cleaned_climate_data.csv",
        mime="text/csv",
    )

# ==============================================================================
# PAGE 2: Statistical Analysis
# ==============================================================================
elif page == "📈 Statistical Analysis":
    st.markdown('<div class="main-title">📈 Statistical Summary & Aggregates</div>', unsafe_allow_html=True)
    st.write("Descriptive statistics summarize the central tendency, dispersion, and shape of the dataset's distribution. Below is the numerical profile of the climate dataset:")
    
    # Display pandas describe() summary nicely
    st.markdown('<div class="section-header">📊 Descriptive Statistics Table</div>', unsafe_allow_html=True)
    numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        local_summary = filtered_df[numeric_cols].describe()
        st.dataframe(local_summary.style.format(precision=2), use_container_width=True)
    else:
        st.warning("No numeric columns present to calculate summary stats.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">🌧️ Rainfall Aggregates</div>', unsafe_allow_html=True)
        if "Rainfall (mm)" in filtered_df.columns:
            st.write(f"- **Total Cumulative Rainfall**: `{filtered_df['Rainfall (mm)'].sum():.1f} mm`")
            st.write(f"- **Daily Average Rainfall**: `{filtered_df['Rainfall (mm)'].mean():.2f} mm`")
            st.write(f"- **Maximum Precipitation in 24 hrs**: `{filtered_df['Rainfall (mm)'].max():.1f} mm`")
            
            if "Month_Name" in filtered_df.columns:
                monthly_rain = filtered_df.groupby("Month_Name")["Rainfall (mm)"].sum()
                if not monthly_rain.empty:
                    st.write(f"- **Highest Rainfall Month (Filtered Data)**: `{monthly_rain.idxmax()} ({monthly_rain.max():.1f} mm)`")
        else:
            st.info("Rainfall column is currently removed.")
        
    with col2:
        st.markdown('<div class="section-header">⛅ Weather Condition Frequencies</div>', unsafe_allow_html=True)
        if "Weather Condition" in filtered_df.columns:
            local_counts = filtered_df["Weather Condition"].value_counts()
            local_pcts = filtered_df["Weather Condition"].value_counts(normalize=True) * 100
            freq_df = pd.DataFrame({
                "Frequency (Days)": local_counts,
                "Percentage Share": local_pcts.map("{:.1f}%".format)
            })
            st.table(freq_df)
        else:
            st.info("Weather Condition column is currently removed.")

# ==============================================================================
# PAGE 3: Visualizations Dashboard (Plotly Upgraded)
# ==============================================================================
elif page == "🎨 Visualizations Dashboard":
    st.markdown('<div class="main-title">🎨 Advanced Visualizations Hub</div>', unsafe_allow_html=True)
    st.write("Browse dynamic, interactive Plotly visualizations across different domains using the tab interface below:")
    
    # Establish tabs for clean visual classification
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌡️ Temp & Humidity", 
        "🌧️ Rainfall & Wind", 
        "⛅ Weather Distributions", 
        "🔗 Physics Models & Correlations"
    ])
    
    # ----------------------------------------------------
    # TAB 1: Temperature & Humidity
    # ----------------------------------------------------
    with tab1:
        st.markdown('<div class="section-header">Temperature & Humidity Timelines</div>', unsafe_allow_html=True)
        
        # 1. Combined Time Series Line Plot
        has_temp = "Temperature (°C)" in filtered_df.columns
        has_hum = "Humidity (%)" in filtered_df.columns
        
        if has_temp or has_hum:
            fig_line = go.Figure()
            
            if has_temp:
                # Add daily temperature points
                fig_line.add_trace(go.Scatter(
                    x=filtered_df["Date"], y=filtered_df["Temperature (°C)"],
                    mode="lines", name="Daily Temperature",
                    line=dict(color="#FF8A8A", width=1), opacity=0.4
                ))
                # Add smoothed rolling average
                df_temp_roll = filtered_df.set_index("Date")["Temperature (°C)"].rolling(window=rolling_window, center=True).mean()
                fig_line.add_trace(go.Scatter(
                    x=df_temp_roll.index, y=df_temp_roll.values,
                    mode="lines", name=f"Temp {rolling_window}-Day Rolling Avg",
                    line=dict(color="#EF4444", width=2.5)
                ))
                
            if has_hum:
                # Add daily humidity points
                fig_line.add_trace(go.Scatter(
                    x=filtered_df["Date"], y=filtered_df["Humidity (%)"],
                    mode="lines", name="Daily Humidity",
                    line=dict(color="#93C5FD", width=1), opacity=0.4,
                    yaxis="y2"
                ))
                # Add smoothed rolling average
                df_hum_roll = filtered_df.set_index("Date")["Humidity (%)"].rolling(window=rolling_window, center=True).mean()
                fig_line.add_trace(go.Scatter(
                    x=df_hum_roll.index, y=df_hum_roll.values,
                    mode="lines", name=f"Humidity {rolling_window}-Day Rolling Avg",
                    line=dict(color="#3B82F6", width=2.5),
                    yaxis="y2"
                ))
                
            # Layout configuration for dual-axis timeline
            fig_line.update_layout(
                title=dict(text=f"Temperature and Humidity Trends ({rolling_window}-Day Rolling Smoothing)", font=dict(size=16)),
                xaxis=dict(title="Date", rangeslider=dict(visible=True)),
                yaxis=dict(
                    title=dict(text="Temperature (°C)", font=dict(color="#EF4444")),
                    tickfont=dict(color="#EF4444")
                ),
                yaxis2=dict(
                    title=dict(text="Humidity (%)", font=dict(color="#3B82F6")),
                    tickfont=dict(color="#3B82F6"),
                    anchor="x", overlaying="y", side="right"
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified",
                height=550
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("Both Temperature and Humidity columns have been removed. Line charts unavailable.")
            
        # 2. Box Plots for Ranges & Outliers
        st.markdown('<div class="section-header">Monthly Range and Distribution boxplots</div>', unsafe_allow_html=True)
        box_col1, box_col2 = st.columns(2)
        
        with box_col1:
            if has_temp and "Month_Name" in filtered_df.columns:
                fig_box_temp = px.box(
                    filtered_df, x="Month_Name", y="Temperature (°C)",
                    title="Monthly Temperature Distributions (Ranges & Outliers)",
                    points="outliers", color_discrete_sequence=["#EF4444"],
                    category_orders={"Month_Name": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}
                )
                fig_box_temp.update_layout(height=400)
                st.plotly_chart(fig_box_temp, use_container_width=True)
            else:
                st.info("Temperature boxplot unavailable.")
                
        with box_col2:
            if has_hum and "Month_Name" in filtered_df.columns:
                fig_box_hum = px.box(
                    filtered_df, x="Month_Name", y="Humidity (%)",
                    title="Monthly Humidity Distributions (Ranges & Outliers)",
                    points="outliers", color_discrete_sequence=["#3B82F6"],
                    category_orders={"Month_Name": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}
                )
                fig_box_hum.update_layout(height=400)
                st.plotly_chart(fig_box_hum, use_container_width=True)
            else:
                st.info("Humidity boxplot unavailable.")

    # ----------------------------------------------------
    # TAB 2: Rainfall & Wind
    # ----------------------------------------------------
    with tab2:
        st.markdown('<div class="section-header">Rainfall & Wind Analysis</div>', unsafe_allow_html=True)
        
        col_rain, col_wind = st.columns(2)
        
        with col_rain:
            # 1. Rainfall Bar Chart grouped by Year
            if "Rainfall (mm)" in filtered_df.columns and "Month_Name" in filtered_df.columns and "Year" in filtered_df.columns:
                fig_rain = px.bar(
                    filtered_df, x="Month_Name", y="Rainfall (mm)", color="Year",
                    title="Rainfall Distribution by Month and Year",
                    barmode="group", color_continuous_scale=px.colors.sequential.Blues,
                    category_orders={"Month_Name": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}
                )
                fig_rain.update_layout(height=400)
                st.plotly_chart(fig_rain, use_container_width=True)
            else:
                st.info("Rainfall bar chart unavailable.")
                
        with col_wind:
            # 2. Monthly Wind Speed Box Plots
            if "Wind Speed (km/h)" in filtered_df.columns and "Month_Name" in filtered_df.columns:
                fig_wind = px.box(
                    filtered_df, x="Month_Name", y="Wind Speed (km/h)",
                    title="Wind Speed Variations by Month",
                    color_discrete_sequence=["#10B981"],
                    category_orders={"Month_Name": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}
                )
                fig_wind.update_layout(height=400)
                st.plotly_chart(fig_wind, use_container_width=True)
            else:
                st.info("Wind speed boxplot unavailable.")
                
        # 3. Wind Speed vs Pressure Scatter (Storm Tracker)
        st.markdown('<div class="section-header">Storm Tracker Physics Model</div>', unsafe_allow_html=True)
        has_wind = "Wind Speed (km/h)" in filtered_df.columns
        has_press = "Atmospheric Pressure (hPa)" in filtered_df.columns
        
        if has_wind and has_press:
            # Safely select active columns for this plot and drop NaNs to avoid statsmodels OLS ValueError
            plot_cols = ["Atmospheric Pressure (hPa)", "Wind Speed (km/h)"]
            if "Weather Condition" in filtered_df.columns:
                plot_cols.append("Weather Condition")
            if "Date" in filtered_df.columns:
                plot_cols.append("Date")
            if "Rainfall (mm)" in filtered_df.columns:
                plot_cols.append("Rainfall (mm)")
                
            plot_df = filtered_df[plot_cols].dropna()
            has_enough_points = len(plot_df) > 2
            
            # Generate scatter plot with trendline
            fig_scatter_storm = px.scatter(
                plot_df, x="Atmospheric Pressure (hPa)", y="Wind Speed (km/h)",
                color="Weather Condition" if "Weather Condition" in plot_df.columns else None,
                color_discrete_map=colors_map,
                title="Wind Speed vs. Atmospheric Pressure (Physical Storm Indicators)",
                trendline="ols" if (has_enough_points and "Weather Condition" not in columns_to_remove) else None,
                hover_data=["Date", "Rainfall (mm)"] if "Rainfall (mm)" in plot_df.columns else ["Date"]
            )
            fig_scatter_storm.update_layout(height=450)
            st.plotly_chart(fig_scatter_storm, use_container_width=True)
        else:
            st.info("Wind Speed and Atmospheric Pressure scatter plot requires both columns to be present.")

    # ----------------------------------------------------
    # TAB 3: Weather Distributions
    # ----------------------------------------------------
    with tab3:
        st.markdown('<div class="section-header">Weather Condition Proportions</div>', unsafe_allow_html=True)
        
        if "Weather Condition" in filtered_df.columns:
            dist_col1, dist_col2 = st.columns(2)
            
            with dist_col1:
                # 1. Donut Pie Chart (Overall Distribution)
                counts = filtered_df["Weather Condition"].value_counts()
                fig_donut = go.Figure(data=[go.Pie(
                    labels=counts.index, values=counts.values, hole=.4,
                    marker=dict(colors=[colors_map.get(k, "#10B981") for k in counts.index])
                )])
                fig_donut.update_layout(title_text="Total Weather Proportions Share", height=400)
                st.plotly_chart(fig_donut, use_container_width=True)
                
            with dist_col2:
                # 2. Monthly Weather Condition Proportions (Stacked Bar)
                if "Month_Name" in filtered_df.columns:
                    monthly_dist = filtered_df.groupby(["Month_Name", "Weather Condition"]).size().reset_index(name="Days")
                    fig_stacked = px.bar(
                        monthly_dist, x="Month_Name", y="Days", color="Weather Condition",
                        title="Seasonal Weather Condition Proportions by Month",
                        color_discrete_map=colors_map,
                        barmode="relative",
                        category_orders={"Month_Name": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}
                    )
                    fig_stacked.update_layout(height=400)
                    st.plotly_chart(fig_stacked, use_container_width=True)
        else:
            st.warning("Weather Condition column has been removed. Distribution charts unavailable.")

    # ----------------------------------------------------
    # TAB 4: Correlation & Physics
    # ----------------------------------------------------
    with tab4:
        st.markdown('<div class="section-header">Climate Physics Scatter Models</div>', unsafe_allow_html=True)
        
        has_temp = "Temperature (°C)" in filtered_df.columns
        has_hum = "Humidity (%)" in filtered_df.columns
        
        if has_temp and has_hum:
            # Safely select active columns for this plot and drop NaNs to avoid statsmodels OLS ValueError
            plot_cols = ["Temperature (°C)", "Humidity (%)"]
            if "Weather Condition" in filtered_df.columns:
                plot_cols.append("Weather Condition")
            if "Date" in filtered_df.columns:
                plot_cols.append("Date")
            if "Rainfall (mm)" in filtered_df.columns:
                plot_cols.append("Rainfall (mm)")
                
            plot_df = filtered_df[plot_cols].dropna()
            has_enough_points = len(plot_df) > 2
            
            # 1. Temperature vs Humidity Scatter Plot
            fig_scatter_th = px.scatter(
                plot_df, x="Temperature (°C)", y="Humidity (%)",
                color="Weather Condition" if "Weather Condition" in plot_df.columns else None,
                color_discrete_map=colors_map,
                title="Relative Humidity vs. Temperature (Inverse Psychrometric Scatter)",
                trendline="ols" if (has_enough_points and "Weather Condition" not in columns_to_remove) else None,
                hover_data=["Date", "Rainfall (mm)"] if "Rainfall (mm)" in plot_df.columns else ["Date"]
            )
            fig_scatter_th.update_layout(height=450)
            st.plotly_chart(fig_scatter_th, use_container_width=True)
        else:
            st.info("Temperature and Humidity correlation scatter plot requires both columns to be present.")
            
        # 2. Interactive Correlation Matrix Heatmap
        st.markdown('<div class="section-header">Interactive Correlation Heatmap</div>', unsafe_allow_html=True)
        corr_cols = [c for c in ["Temperature (°C)", "Humidity (%)", "Rainfall (mm)", "Wind Speed (km/h)", "Atmospheric Pressure (hPa)"] if c in filtered_df.columns]
        
        if len(corr_cols) > 1:
            corr_matrix = filtered_df[corr_cols].corr()
            
            # Custom styled heatmap with text annotations
            fig_heatmap = ff_fig = px.imshow(
                corr_matrix,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1, zmax=1,
                title="Pearson Correlation Coefficients Matrix"
            )
            fig_heatmap.update_layout(height=450)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.warning("Heatmap requires at least 2 remaining numeric columns to display.")
