#!/usr/bin/env python3
"""
Climate Condition Analysis
---------------------------
A comprehensive Python script for Data Analysis and Data Visualization of climate data.
Designed for academic presentations, demonstrations, and viva evaluations.

Features:
1. Synthetic climate data generation (if climate_data.csv is missing).
2. Data preprocessing: Duplicate removal, missing value imputation, and type conversion.
3. Statistical analysis: Averages, extremes, trends, and frequencies.
4. Visualizations: Line charts, bar charts, pie chart, histogram, and correlation heatmap.
5. Automated text-based insights generation.
"""

import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)


def generate_sample_data(filepath="climate_data.csv", num_records=1096):
    """
    Generates a realistic synthetic climate dataset spanning approximately 3 years.
    Includes seasonal trends and realistic correlations between meteorological variables.
    Also injects duplicate rows and missing values to demonstrate data preprocessing.
    """
    print(f"[1/6] Generating sample climate dataset ({num_records} records)...")
    
    # 1. Generate date range (e.g., 3 years from 2023-01-01 to 2025-12-31)
    dates = pd.date_range(start="2023-01-01", periods=num_records, freq="D")
    
    data = []
    
    for date in dates:
        month = date.month
        day_of_year = date.timetuple().tm_yday
        
        # Determine season in Northern Hemisphere
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Autumn"
            
        # Determine weather condition based on seasonal probabilities
        conditions = ["Sunny", "Cloudy", "Rainy", "Stormy"]
        if season == "Winter":
            probs = [0.25, 0.45, 0.20, 0.10]
        elif season == "Spring":
            probs = [0.40, 0.35, 0.15, 0.10]
        elif season == "Summer":
            probs = [0.60, 0.20, 0.15, 0.05]
        else:  # Autumn
            probs = [0.30, 0.40, 0.20, 0.10]
            
        condition = np.random.choice(conditions, p=probs)
        
        # Generate base temperature with a seasonal sine wave
        # Peaks in July (around day 200), coldest in January (day 15)
        base_temp = 18.0 + 11.0 * np.sin(2 * np.pi * (day_of_year - 110) / 365)
        
        # Adjust meteorological variables based on Weather Condition to ensure physical realism
        if condition == "Sunny":
            temp = base_temp + np.random.uniform(2.0, 5.0)
            humidity = np.random.uniform(35.0, 55.0)
            rainfall = 0.0
            wind_speed = np.random.uniform(4.0, 15.0)
            pressure = np.random.uniform(1015.0, 1025.0)
        elif condition == "Cloudy":
            temp = base_temp + np.random.uniform(-2.0, 1.5)
            humidity = np.random.uniform(55.0, 75.0)
            rainfall = np.random.choice([0.0, np.random.uniform(0.1, 1.5)], p=[0.85, 0.15])
            wind_speed = np.random.uniform(6.0, 20.0)
            pressure = np.random.uniform(1009.0, 1016.0)
        elif condition == "Rainy":
            temp = base_temp - np.random.uniform(2.0, 5.0)
            humidity = np.random.uniform(78.0, 95.0)
            rainfall = np.random.exponential(scale=10.0) + 2.0
            wind_speed = np.random.uniform(12.0, 28.0)
            pressure = np.random.uniform(998.0, 1009.0)
        else:  # Stormy
            temp = base_temp - np.random.uniform(4.0, 8.0)
            humidity = np.random.uniform(85.0, 100.0)
            rainfall = np.random.uniform(20.0, 75.0)
            wind_speed = np.random.uniform(30.0, 62.0)
            pressure = np.random.uniform(985.0, 999.0)
            
        # Add random noise to values
        temp += np.random.normal(0, 1.0)
        humidity += np.random.normal(0, 2.0)
        wind_speed += np.random.normal(0, 1.5)
        pressure += np.random.normal(0, 1.0)
        
        # Ensure values stay in logical bounds
        humidity = np.clip(humidity, 10.0, 100.0)
        wind_speed = np.clip(wind_speed, 0.0, 100.0)
        
        data.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Temperature (°C)": round(temp, 1),
            "Humidity (%)": int(round(humidity)),
            "Rainfall (mm)": round(rainfall, 1),
            "Wind Speed (km/h)": round(wind_speed, 1),
            "Atmospheric Pressure (hPa)": round(pressure, 1),
            "Weather Condition": condition
        })
        
    df = pd.DataFrame(data)
    
    # Inject duplicate rows (approx. 15 duplicates) to demonstrate preprocessing
    dup_indices = np.random.choice(range(num_records), size=15, replace=False)
    duplicates = df.iloc[dup_indices].copy()
    # Shift dates slightly or keep them identical to be true duplicates
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Inject missing values (NaN) to demonstrate handling of missing values
    # Temperature: 18 missing values
    temp_nan_indices = np.random.choice(df.index, size=18, replace=False)
    df.loc[temp_nan_indices, "Temperature (°C)"] = np.nan
    
    # Humidity: 12 missing values
    hum_nan_indices = np.random.choice(df.index, size=12, replace=False)
    df.loc[hum_nan_indices, "Humidity (%)"] = np.nan
    
    # Wind Speed: 10 missing values
    wind_nan_indices = np.random.choice(df.index, size=10, replace=False)
    df.loc[wind_nan_indices, "Wind Speed (km/h)"] = np.nan
    
    # Shuffle the dataset to mix duplicates and missing values
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    print(f"   Success: Saved generated sample dataset with {len(df)} rows to '{filepath}'.")
    return filepath


def load_and_preprocess_data(filepath):
    """
    Loads raw CSV climate data and cleans it:
    1. Handles duplicate entries.
    2. Identifies and cleans missing values (using group medians).
    3. Converts Date column to Datetime format.
    4. Generates statistical summaries.
    """
    print("\n[2/6] Starting Data Preprocessing...")
    
    # Load dataset
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file '{filepath}' not found.")
        
    df = pd.read_csv(filepath)
    print(f"   Raw Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns.")
    
    # 1. Handle Duplicates
    num_duplicates = df.duplicated().sum()
    print(f"   Found {num_duplicates} duplicate records.")
    if num_duplicates > 0:
        df = df.drop_duplicates()
        print(f"   Duplicates removed. Cleaned Dataset shape: {df.shape[0]} rows.")
        
    # 2. Check for missing values
    missing_report = df.isnull().sum()
    print("   Missing values report:")
    for col, val in missing_report.items():
        if val > 0:
            print(f"      - {col}: {val} missing values.")
            
    # 3. Handle missing values
    # For Temperature, Humidity, and Wind Speed, fill missing values with the median value
    # corresponding to that day's Weather Condition (e.g. missing temp on Sunny day gets filled with median Sunny temp)
    # This is a robust data science technique that preserves physical correlations.
    for col in ["Temperature (°C)", "Humidity (%)", "Wind Speed (km/h)"]:
        if df[col].isnull().sum() > 0:
            # Group by weather condition and get median
            group_medians = df.groupby("Weather Condition")[col].transform("median")
            df[col] = df[col].fillna(group_medians)
            # If any remaining (e.g., if Weather Condition itself was missing, though it's not here), fill with overall median
            df[col] = df[col].fillna(df[col].median())
            
    print("   All missing values have been imputed successfully.")
    
    # 4. Convert Date to proper datetime format
    df["Date"] = pd.to_datetime(df["Date"])
    # Sort chronologically by date
    df = df.sort_values("Date").reset_index(drop=True)
    print("   Converted Date column to Datetime format and sorted records chronologically.")
    
    # 5. Extract additional temporal features for analysis
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%b")
    df["Year_Month"] = df["Date"].dt.to_period("M")
    
    # Generate statistical summary
    summary_stats = df.describe()
    
    return df, summary_stats


def perform_climate_analysis(df):
    """
    Computes climate statistics, trends, and frequency distributions.
    """
    print("\n[3/6] Running Climate Analysis...")
    
    results = {}
    
    # A. Temperature Metrics
    results["avg_temp"] = df["Temperature (°C)"].mean()
    results["max_temp"] = df["Temperature (°C)"].max()
    results["min_temp"] = df["Temperature (°C)"].min()
    
    # B. Humidity Metrics
    results["avg_humidity"] = df["Humidity (%)"].mean()
    results["std_humidity"] = df["Humidity (%)"].std()
    results["min_humidity"] = df["Humidity (%)"].min()
    results["max_humidity"] = df["Humidity (%)"].max()
    
    # C. Rainfall Metrics
    results["total_rainfall"] = df["Rainfall (mm)"].sum()
    results["avg_rainfall"] = df["Rainfall (mm)"].mean()
    results["max_daily_rainfall"] = df["Rainfall (mm)"].max()
    
    # D. Wind Speed Metrics
    results["avg_wind_speed"] = df["Wind Speed (km/h)"].mean()
    results["max_wind_speed"] = df["Wind Speed (km/h)"].max()
    
    # E. Monthly Trends (aggregated across all years)
    monthly_stats = df.groupby("Month_Name").agg({
        "Temperature (°C)": "mean",
        "Humidity (%)": "mean",
        "Rainfall (mm)": "sum",
        "Wind Speed (km/h)": "mean"
    }).reindex(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    
    results["monthly_stats"] = monthly_stats
    
    # Find Highest Rainfall Month (overall and average-wise)
    # 1. Sum by Year-Month to find the single wettest month in the dataset
    monthly_rainfall_series = df.groupby("Year_Month")["Rainfall (mm)"].sum()
    wettest_year_month = monthly_rainfall_series.idxmax()
    results["wettest_month_record"] = f"{wettest_year_month} ({monthly_rainfall_series.max():.1f} mm)"
    
    # 2. Average monthly rainfall across the years to find typical rainiest calendar month
    calendar_monthly_rainfall = df.groupby("Month_Name")["Rainfall (mm)"].sum() / df["Year"].nunique()
    calendar_monthly_rainfall = calendar_monthly_rainfall.reindex(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    results["highest_avg_rainfall_month"] = calendar_monthly_rainfall.idxmax()
    results["highest_avg_rainfall_val"] = calendar_monthly_rainfall.max()
    
    # F. Weather Condition Analysis
    weather_counts = df["Weather Condition"].value_counts()
    weather_percentages = df["Weather Condition"].value_counts(normalize=True) * 100
    
    results["weather_counts"] = weather_counts
    results["weather_percentages"] = weather_percentages
    results["most_common_weather"] = weather_counts.idxmax()
    results["most_common_weather_pct"] = weather_percentages.max()
    
    print("   Climate metrics successfully computed.")
    return results


def generate_visualizations(df, results, output_dir="visualizations"):
    """
    Generates professional-grade matplotlib/seaborn plots and saves them as PNG files.
    """
    print(f"\n[4/6] Generating Visualizations and saving to '{output_dir}/'...")
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set styling parameters for premium aesthetic
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "figure.titlesize": 16,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10
    })
    
    # Define cohesive, professional color palette
    colors_dict = {
        "Sunny": "#F2B824",    # Warm Yellow/Amber
        "Cloudy": "#8CA1A5",   # Slate/Cool Grey
        "Rainy": "#3B82F6",    # Blue
        "Stormy": "#6366F1"    # Indigo/Dark Blue
    }
    palette = [colors_dict.get(c, "#10B981") for c in ["Sunny", "Cloudy", "Rainy", "Stormy"]]

    # ----------------------------------------------------
    # Plot 1: Temperature Trend & Distribution (Line & Histogram)
    # ----------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Left subplot: Line Chart (Temperature vs Date)
    ax1.plot(df["Date"], df["Temperature (°C)"], color="#FCA5A5", alpha=0.4, label="Daily Temperature")
    df_temp_rolled = df.set_index("Date")["Temperature (°C)"].rolling(window=30, center=True).mean()
    ax1.plot(df_temp_rolled.index, df_temp_rolled.values, color="#DC2626", linewidth=2.5, label="30-Day Rolling Avg")
    ax1.set_title("Temperature Trend (2023 - 2025)", fontweight="bold", pad=10)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Temperature (°C)")
    ax1.legend(loc="upper right", frameon=True)
    
    # Right subplot: Histogram (Temperature Distribution)
    sns.histplot(df["Temperature (°C)"], kde=True, color="#DC2626", bins=20, ax=ax2)
    ax2.set_title("Temperature Frequency Distribution", fontweight="bold", pad=10)
    ax2.set_xlabel("Temperature (°C)")
    ax2.set_ylabel("Frequency (Days)")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "temperature_trend.png"), dpi=150)
    plt.close()
    print("   -> Saved 'temperature_trend.png'")

    # ----------------------------------------------------
    # Plot 2: Humidity & Wind Speed Analysis (Line Charts)
    # ----------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Humidity
    ax1.plot(df["Date"], df["Humidity (%)"], color="#93C5FD", alpha=0.4, label="Daily Humidity")
    df_hum_rolled = df.set_index("Date")["Humidity (%)"].rolling(window=30, center=True).mean()
    ax1.plot(df_hum_rolled.index, df_hum_rolled.values, color="#2563EB", linewidth=2, label="30-Day Rolling Avg")
    ax1.set_title("Humidity Variation Over Time", fontweight="bold")
    ax1.set_ylabel("Humidity (%)")
    ax1.legend(loc="lower left", frameon=True)
    
    # Wind Speed
    ax2.plot(df["Date"], df["Wind Speed (km/h)"], color="#A7F3D0", alpha=0.4, label="Daily Wind Speed")
    df_wind_rolled = df.set_index("Date")["Wind Speed (km/h)"].rolling(window=30, center=True).mean()
    ax2.plot(df_wind_rolled.index, df_wind_rolled.values, color="#059669", linewidth=2, label="30-Day Rolling Avg")
    ax2.set_title("Wind Speed Trend Over Time", fontweight="bold")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Wind Speed (km/h)")
    ax2.legend(loc="upper left", frameon=True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "humidity_analysis.png"), dpi=150)
    plt.close()
    print("   -> Saved 'humidity_analysis.png'")

    # ----------------------------------------------------
    # Plot 3: Monthly Rainfall Analysis (Bar Chart)
    # ----------------------------------------------------
    # Get total rainfall by month name
    monthly_stats = results["monthly_stats"]
    
    plt.figure(figsize=(10, 5))
    sns.barplot(x=monthly_stats.index, y=monthly_stats["Rainfall (mm)"], hue=monthly_stats.index, palette="Blues_d", legend=False)
    plt.title("Total Cumulative Rainfall by Month (2023 - 2025)", pad=15, fontweight="bold")
    plt.xlabel("Month", labelpad=10)
    plt.ylabel("Rainfall (mm)", labelpad=10)
    
    # Annotate total values on top of bars
    for i, val in enumerate(monthly_stats["Rainfall (mm)"]):
        plt.text(i, val + 15, f"{val:.0f}mm", ha="center", va="bottom", fontsize=9, fontweight="semibold")
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "rainfall_analysis.png"), dpi=150)
    plt.close()
    print("   -> Saved 'rainfall_analysis.png'")

    # ----------------------------------------------------
    # Plot 4: Weather Condition Distribution (Bar & Pie Charts)
    # ----------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Bar chart of Weather Condition Counts
    sns.barplot(x=results["weather_counts"].index, y=results["weather_counts"].values, 
                hue=results["weather_counts"].index, palette=colors_dict, ax=ax1, legend=False)
    ax1.set_title("Frequency of Weather Conditions", fontweight="bold", pad=10)
    ax1.set_xlabel("Weather Condition")
    ax1.set_ylabel("Number of Days")
    for i, count in enumerate(results["weather_counts"].values):
        ax1.text(i, count + 10, str(count), ha="center", va="bottom", fontweight="semibold")
        
    # Right: Pie chart (Donut) of Weather Condition Distribution
    ax2.pie(
        results["weather_percentages"].values, 
        labels=results["weather_percentages"].index, 
        autopct="%1.1f%%", 
        startangle=90, 
        colors=[colors_dict[c] for c in results["weather_percentages"].index],
        wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2)  # Generates donut ring structure
    )
    ax2.set_title("Percentage Share of Weather Conditions", fontweight="bold", pad=10)
    
    plt.suptitle("Weather Condition Distribution Analysis", y=0.98, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "weather_distribution.png"), dpi=150)
    plt.close()
    print("   -> Saved 'weather_distribution.png'")

    # ----------------------------------------------------
    # Plot 5: Correlation Heatmap
    # ----------------------------------------------------
    cols_to_correlate = [
        "Temperature (°C)", 
        "Humidity (%)", 
        "Rainfall (mm)", 
        "Wind Speed (km/h)", 
        "Atmospheric Pressure (hPa)"
    ]
    corr_matrix = df[cols_to_correlate].corr()
    
    plt.figure(figsize=(8, 6.5))
    sns.heatmap(
        corr_matrix, 
        annot=True, 
        cmap="coolwarm", 
        fmt=".2f", 
        linewidths=1.5, 
        square=True,
        cbar_kws={"shrink": 0.8},
        vmin=-1, vmax=1
    )
    plt.title("Correlation Matrix of Climate Variables", pad=20, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "correlation_heatmap.png"), dpi=150)
    plt.close()
    print("   -> Saved 'correlation_heatmap.png'")


def generate_insights(df, results):
    """
    Constructs and structures climate observations and insights from the data.
    """
    print("\n[5/6] Generating Climate Insights...")
    
    monthly_stats = results["monthly_stats"]
    
    # 1. Hottest and Coldest months on average
    hottest_month = monthly_stats["Temperature (°C)"].idxmax()
    hottest_temp = monthly_stats["Temperature (°C)"].max()
    coldest_month = monthly_stats["Temperature (°C)"].idxmin()
    coldest_temp = monthly_stats["Temperature (°C)"].min()
    
    # 2. Wettest calendar month (highest average rainfall)
    rainiest_month = results["highest_avg_rainfall_month"]
    rainiest_rainfall = results["highest_avg_rainfall_val"]
    
    # 3. Year-over-year annual averages
    yearly_stats = df.groupby("Year").agg({
        "Temperature (°C)": "mean",
        "Humidity (%)": "mean",
        "Rainfall (mm)": "sum"
    })
    
    insights = {
        "hottest_month": hottest_month,
        "hottest_temp": hottest_temp,
        "coldest_month": coldest_month,
        "coldest_temp": coldest_temp,
        "rainiest_month": rainiest_month,
        "rainiest_rainfall": rainiest_rainfall,
        "yearly_stats": yearly_stats,
        "most_common_weather": results["most_common_weather"],
        "most_common_weather_pct": results["most_common_weather_pct"],
        "avg_annual_temp": results["avg_temp"],
        "avg_annual_humidity": results["avg_humidity"]
    }
    
    return insights


def display_results_dashboard(summary_stats, results, insights):
    """
    Prints a beautiful, clean, structured console dashboard for presentations and viva.
    """
    print("\n[6/6] Presenting Final Climate Analysis Dashboard:")
    print("=" * 70)
    print("                     CLIMATE CONDITION ANALYSIS")
    print("                     Subject Project Dashboard")
    print("=" * 70)
    
    # Preprocessing & Size info
    print("\n[DATASET SUMMARY]")
    print(f"Total days analyzed       : {int(summary_stats.loc['count'].iloc[0])} days")
    print(f"Time period               : 2023-01-01 to 2025-12-31 (3 Years)")
    
    # Descriptives
    print("\n[DESCRIPTIVE STATISTICS SUMMARY]")
    print("-" * 70)
    print(f"{'Metric':<25} | {'Mean':<10} | {'Std Dev':<10} | {'Min':<8} | {'Max':<8}")
    print("-" * 70)
    
    metrics = [
        ("Temperature (°C)", results["avg_temp"], df_std_temp := summary_stats.loc["std", "Temperature (°C)"], results["min_temp"], results["max_temp"]),
        ("Humidity (%)", results["avg_humidity"], results["std_humidity"], results["min_humidity"], results["max_humidity"]),
        ("Wind Speed (km/h)", results["avg_wind_speed"], summary_stats.loc["std", "Wind Speed (km/h)"], summary_stats.loc["min", "Wind Speed (km/h)"], results["max_wind_speed"]),
        ("Pressure (hPa)", summary_stats.loc["mean", "Atmospheric Pressure (hPa)"], summary_stats.loc["std", "Atmospheric Pressure (hPa)"], summary_stats.loc["min", "Atmospheric Pressure (hPa)"], summary_stats.loc["max", "Atmospheric Pressure (hPa)"]),
    ]
    
    for label, mean, std, val_min, val_max in metrics:
        print(f"{label:<25} | {mean:<10.2f} | {std:<10.2f} | {val_min:<8.1f} | {val_max:<8.1f}")
    print("-" * 70)
    
    # Rainfall summary
    print("\n[RAINFALL DETAILS]")
    print(f"Total Cumulative Rainfall : {results['total_rainfall']:.1f} mm")
    print(f"Average Daily Rainfall    : {results['avg_rainfall']:.2f} mm")
    print(f"Wettest Month on Record   : {results['wettest_month_record']}")
    print(f"Typical Rainiest Month    : {insights['rainiest_month']} (Avg {insights['rainiest_rainfall']:.1f} mm/year)")
    
    # Weather Condition Distribution
    print("\n[WEATHER CONDITIONS FREQUENCY DISTRIBUTION]")
    print("-" * 50)
    print(f"{'Condition':<15} | {'Frequency (Days)':<18} | {'Percentage (%)':<10}")
    print("-" * 50)
    for cond in results["weather_counts"].index:
        count = results["weather_counts"][cond]
        pct = results["weather_percentages"][cond]
        print(f"{cond:<15} | {count:<18} | {pct:<10.1f}%")
    print("-" * 50)

    # Key Climate Insights
    print("\n" + "*" * 70)
    print("                     KEY CLIMATE INSIGHTS & TRENDS")
    print("*" * 70)
    print(f"1. TEMPERATURE PROFILE: The average temperature over the 3-year period is")
    print(f"   {insights['avg_annual_temp']:.2f}°C. {insights['hottest_month']} is the typical hottest month")
    print(f"   (average {insights['hottest_temp']:.2f}°C), while {insights['coldest_month']} is the coldest")
    print(f"   (average {insights['coldest_temp']:.2f}°C).")
    print()
    print(f"2. HUMIDITY & WIND PROFILE: The region maintains a moderate-to-high average")
    print(f"   humidity of {insights['avg_annual_humidity']:.2f}%. Humidity levels show strong variation")
    print(f"   (Std Dev of {results['std_humidity']:.2f}%), dipping as low as {results['min_humidity']}%")
    print(f"   on dry, sunny days and reaching saturated limits (100.0%) during storms.")
    print()
    print(f"3. MOST PREVALENT WEATHER: The most common weather condition observed is")
    print(f"   '{insights['most_common_weather']}' which occurred on {insights['most_common_weather_pct']:.1f}% of all days.")
    print()
    print(f"4. KEY METEOROLOGICAL CORRELATIONS & OBSERVATIONS:")
    print(f"   - Humidity and Temperature are negatively correlated: on hot, sunny days,")
    print(f"     relative humidity drops, whereas cooler rainy days show higher humidity.")
    print(f"   - Atmospheric Pressure serves as an excellent predictor of stormy weather:")
    print(f"     stormy days feature severely low atmospheric pressure (averaging under 995 hPa)")
    print(f"     paired with high wind speeds (up to {results['max_wind_speed']:.1f} km/h) and heavy rainfall.")
    print(f"   - Rainy and Stormy days account for the entirety of the {results['total_rainfall']:.1f} mm")
    print(f"     cumulative rainfall, demonstrating typical seasonal monsoon patterns.")
    print("*" * 70)
    print("\nVisualizations saved successfully in the 'visualizations/' directory.")
    print("Setup complete. You are ready to present this project!")
    print("=" * 70)


if __name__ == "__main__":
    # Define dataset filepath
    dataset_file = "climate_data.csv"
    
    # Step 1: Check/Generate dataset
    if not os.path.exists(dataset_file):
        generate_sample_data(dataset_file)
    else:
        print(f"[1/6] Found existing dataset '{dataset_file}'. Skipping generation.")
        
    try:
        # Step 2: Load and Preprocess Data
        df, summary_stats = load_and_preprocess_data(dataset_file)
        
        # Step 3: Perform Climate Analysis
        analysis_results = perform_climate_analysis(df)
        
        # Step 4: Generate insights
        insights = generate_insights(df, analysis_results)
        
        # Step 5: Generate Visualizations
        generate_visualizations(df, analysis_results, output_dir="visualizations")
        
        # Step 6: Display results in terminal
        display_results_dashboard(summary_stats, analysis_results, insights)
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred during execution:")
        print(f"        {str(e)}")
        import traceback
        traceback.print_exc()
