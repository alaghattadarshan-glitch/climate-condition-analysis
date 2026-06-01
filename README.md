# Climate Condition Analysis

A Python-based Data Analysis and Data Visualization project designed for academic presentation and evaluation. This project analyzes a multi-year climate dataset, performs data cleaning/preprocessing, calculates descriptive statistics, generates key insights, and exports presentation-ready visualizations.

---

## 🌟 Project Highlights
* **Comprehensive Pipeline**: Covers Data Generation, Preprocessing (duplicate removal & missing value imputation), Statistical Analysis, Visualization, and Insight extraction.
* **Realistic Weather Physics**: The generated dataset models meteorologically consistent correlations (e.g., negative correlation between temperature and humidity; low atmospheric pressure and high wind speed during storms).
* **Academic & Viva Ready**: Includes structured console dashboard output and a curated list of Viva Questions at the end of this document.

---

## 📊 Dataset Schema
The dataset contains the following columns:
1. **Date**: Chronological timestamp of the observation (`YYYY-MM-DD`).
2. **Temperature (°C)**: Ambient temperature (ranges from winter lows of ~2°C to summer highs of ~38°C).
3. **Humidity (%)**: Relative humidity percentage (ranges from dry 30% to saturated 100%).
4. **Rainfall (mm)**: Daily precipitation depth (ranges from 0.0mm up to 80.0mm on stormy days).
5. **Wind Speed (km/h)**: Daily wind speed (ranges from 4km/h to 65km/h).
6. **Atmospheric Pressure (hPa)**: Barometric pressure (centered around standard 1013 hPa; drops during rain/storms).
7. **Weather Condition**: Categorical column representing the predominant weather (`Sunny`, `Cloudy`, `Rainy`, `Stormy`).

---

## ⚙️ Preprocessing Strategy
To simulate real-world data issues, the raw dataset intentionally includes duplicates and missing values. The script cleans these using:
1. **Duplicate Removal**: Identifies and drops duplicate rows.
2. **Condition-Aware Imputation**: Missing values in numeric columns (`Temperature`, `Humidity`, `Wind Speed`) are filled with the **median value of that specific weather condition** (e.g., a missing temperature on a "Sunny" day is filled with the median temperature of all "Sunny" days rather than the global median). This maintains physical realism.
3. **Datetime Conversion**: Converts the date column into pandas `datetime` format to enable temporal feature extraction (Months, Years).

---

## 📂 Project Structure
```
Climate_Condition_Analysis/
│
├── climate_data.csv          # Raw & cleaned dataset (1,000+ records)
├── climate_analysis.py       # Main execution Python script
├── dashboard.py              # Interactive Streamlit Web UI Dashboard
├── requirements.txt          # Python dependencies
│
├── visualizations/           # Generated presentation-ready charts
│   ├── temperature_trend.png      # Temperature vs Date & Distribution (subplots)
│   ├── humidity_analysis.png      # Humidity & Wind Speed trends (subplots)
│   ├── rainfall_analysis.png      # Total Rainfall by Month (bar chart)
│   ├── weather_distribution.png   # Frequency & Percentage share (bar & pie donut charts)
│   └── correlation_heatmap.png    # Correlation Matrix heatmap
│
└── README.md                 # Project documentation & Viva Q&A
```

---

## 🚀 Setup and Execution

### 1. Prerequisites
Ensure you have Python 3 installed. You will need the following libraries:
* `pandas`
* `numpy`
* `matplotlib`
* `seaborn`
* `streamlit`
* `plotly`
* `statsmodels`

### 2. Quick Installation
You can install the dependencies using pip:
```bash
pip install pandas numpy matplotlib seaborn streamlit plotly statsmodels
```

*Alternatively, if you are running inside a virtual environment:*
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Project

#### Option A: Command Line Interface (CLI)
Execute the console-based analysis pipeline:
```bash
python climate_analysis.py
```
This will:
1. Generate the sample dataset (`climate_data.csv`) if it doesn't already exist.
2. Perform cleaning (handling duplicates & missing values).
3. Compute all climate statistics.
4. Export static presentation charts inside the `visualizations/` folder.
5. Print a comprehensive, clean ASCII Dashboard directly to the console.

#### Option B: Interactive Web Dashboard (GUI)
Start the Streamlit-based local web app:
```bash
streamlit run dashboard.py
```
This will start a local server and automatically open a web browser tab at `http://localhost:8501`. The dashboard allows you to:
* Filter the dataset interactively by year and weather condition.
* Remove columns dynamically from the active dataframe, updating all KPIs and charts in real-time.
* Smooth timelines dynamically using a rolling average slider (5 to 90 days).
* Browse advanced, fully interactive **Plotly charts** grouped under clean category tabs.

---

## 🔬 Visualizations and Plots

The project generates two types of graphs to accommodate different presentation styles:

### A. Static Presentation Charts (`visualizations/`)
Perfect for copy-pasting into PPT slides, reports, or papers:
1. **`temperature_trend.png`**: Multi-panel line trend vs date (with 30-day rolling avg) and temperature distribution histogram.
2. **`humidity_analysis.png`**: Dual timeline subplots showing Humidity and Wind Speed variation.
3. **`rainfall_analysis.png`**: Bar chart showing total cumulative rainfall grouped by calendar month.
4. **`weather_distribution.png`**: Side-by-side weather condition frequency (bar) and share percentage (donut pie) charts.
5. **`correlation_heatmap.png`**: Divergent correlation heatmap matrix showing physical correlations.

### B. Interactive Dashboard Charts (`dashboard.py`)
Features dynamic tooltips, zooming, panning, and instant filtering:
1. **Temperature & Humidity Tab**:
   * *Dual-Axis Timeline*: Temperature and Humidity plotted together on different y-axes with a range selector slider.
   * *Outlier Boxplots*: Monthly ranges showing box-and-whisker distributions for temperatures and humidity, detecting extreme anomalies.
2. **Rainfall & Wind Tab**:
   * *Precipitation Bar Chart*: Grouped rainfall by month, color-coded by year (2023, 2024, 2025).
   * *Wind Speed Boxplot*: Monthly wind variations.
   * *Storm Scatter Model*: Atmospheric Pressure vs Wind Speed with a fitted linear trendline to visualize storm thresholds.
3. **Weather Distributions Tab**:
   * *Donut Share*: Overall weather condition percentages.
   * *Seasonal Stacked Bar*: Monthly weather condition proportions, showing seasonal transitions.
4. **Physics Models & Correlations Tab**:
   * *Psychrometric Model*: Temperature vs Humidity scatter chart colored by Weather Condition showing physical correlations.
   * *Heatmap*: Pearson correlation matrix displaying interactive tooltips for coefficients.

---

## 🎓 Viva / Presentation Q&A Reference
Prepare for common evaluation questions:

* **Q1: Why did you use median values for missing data instead of mean?**
  * *Answer*: Median is robust to outliers, which are common in weather data (e.g., storms have extreme rainfall and wind). Imputing based on the *Weather Condition* group (e.g., Sunny group vs. Stormy group) ensures we don't fill a missing temperature on a stormy winter day with a hot summer day's average.

* **Q2: What is the purpose of the rolling average in the line charts?**
  * *Answer*: Daily weather data is highly volatile. A rolling average (moving window) smooths out day-to-day noise to clearly display the underlying seasonal climate trends (seasonal cycles).

* **Q3: What does the correlation heatmap tell us about the weather physics in your data?**
  * *Answer*: It confirms physical correlations:
    * Relative humidity decreases as temperature rises (negative correlation).
    * Stormy weather is marked by low atmospheric pressure (negative correlation between pressure and rainfall/wind speed).
    * High wind speeds and rainfall are strongly positively correlated as they typically occur together during storms.

* **Q4: Which libraries were used and why?**
  * *Answer*: 
    * `pandas` for structured data representation, cleaning, and grouping.
    * `numpy` for mathematical operations and synthetic data generation.
    * `matplotlib` for creating figure containers and fine-grained plot customization.
    * `seaborn` for high-level statistical plotting (like heatmaps and styled bar charts).
