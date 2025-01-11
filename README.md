# Data Analysis Web Application

A simple Django web application to analyze CSV files and visualize data with ease.

## Features
- Upload and analyze CSV files directly.
- View head and tail of the dataset, missing values count, variance, standard deviation, covariance, and correlation.
- Generate visualizations (e.g., pairplots) using Seaborn and Matplotlib.
- Perform bivariate analysis and display results interactively.

## Prerequisites
Ensure you have the following installed: Python 3.8+, Django 4.0+, Pandas, Matplotlib, Seaborn.

## Installation
1. Clone the repository: `https://github.com/saraelghou/SaraAnalyzer.git`.
2. Set up the virtual environment: `python -m venv env && source env/bin/activate` (on Windows: `env\Scripts\activate`).
4. Run migrations: `python manage.py migrate`.
5. Start the server: `python manage.py runserver`.
6. Open your browser at `http://127.0.0.1:8000/` to start analyzing data.

## How to Use
1. Navigate to the homepage.
2. Upload your CSV file.
3. Click "Analyze" to process the data.
4. View statistical summaries and visualizations.

## Project Structure
myproject/
│
├── myapp/
│   ├── views.py         # Core logic for analysis
│   ├── templates/       # HTML templates
│   │   ├── upload.html
│   │   ├── analysis.html
│   ├── static/          # Optional static files
│
├── myproject/
│   ├── settings.py      # Django settings
│   ├── urls.py          # URL routing
│
└──  manage.py            # Django management script


## Dependencies
Install all dependencies using: `pip install django pandas matplotlib seaborn`.


