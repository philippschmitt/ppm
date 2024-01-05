import urllib.request
import csv
import os
import shutil
import json
import datetime

def fetch_csv_from_web(url):
    try:
        # Fetch the data from the URL
        response = urllib.request.urlopen(url)
        data = response.read().decode('utf-8')
        return data
    except Exception as e:
        print("An error occurred:", e)
        return None

# Ignore comments in csv file
# Source: https://stackoverflow.com/questions/14158868/python-skip-comment-lines-marked-with-in-csv-dictreader
def decomment(csvfile):
    for row in csvfile:
        raw = row.split('#')[0].strip()
        if raw: yield raw

def iterate_csv_rows(csv_data):
  if csv_data is not None:
      csv_lines = csv_data.splitlines()
      csv_reader = csv.DictReader(decomment(csv_lines))
      return csv_reader
  else:
      print("CSV data is not available.")


def write_json_file(dict, filename):
  try:
    os.makedirs(os.path.dirname(filename))
  except FileExistsError:
    # directory already exists
    pass
  with open(filename, "w") as f:
    json.dump(dict, f)



if __name__ == "__main__":

    # Data Source: https://gml.noaa.gov/ccgg/trends/gl_data.html
    annual_csv_url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_gl.csv"
    monthly_csv_url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.csv"
    daily_csv_url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_trend_gl.csv"

    # API Version 1
    # GET: philippschmitt.github.io/ppm/{YYYY}/{M}
    api_version = "v1"

    # Fetch data
    annual_data = fetch_csv_from_web(annual_csv_url)
    monthly_data = fetch_csv_from_web(monthly_csv_url)
    daily_data = fetch_csv_from_web(daily_csv_url)

    # Delete API folder if it already exists (i.e. previous build)
    shutil.rmtree(os.path.join(os.getcwd(), api_version), ignore_errors=True)

    # Get annual mean atmospheric carbon and store in year folders
    annual = iterate_csv_rows(annual_data)
    for row in annual:
      write_json_file(
        {
          'year': int(row['year']),
          'ppm': float(row['mean']),
        }, 
        os.path.join(os.getcwd(), api_version, row['year'], 'index.json')
      )

    # Get monthly atmospheric carbon and store in month folders
    monthly = iterate_csv_rows(monthly_data)
    monthly_data_latest = {}
    # Calculate annual mean based on current available data
    today = datetime.date.today()
    annual_trend_total = 0.0
    annual_trend_n_samples = 0
    annual_mean_to_date = 0.0

    # Write monthly data
    for row in monthly:
      write_json_file(
        # Create output dictionary
        {
          'year': int(row['year']),
          'month': int(row['month']),
          'ppm': float(row['trend']),
        }, 
        # Create output path
        os.path.join(os.getcwd(), api_version, row['year'], row['month'], 'index.json')
      )
      # Update latest monthly data record
      monthly_data_latest = { 'year': int(row['year']), 'month': int(row['month']) }

      # Calculate the current (up-to-today) annual mean
      if int(row['year']) == today.year:
        annual_trend_total += float(row['trend'])
        annual_trend_n_samples += 1

    # Calculate annual mean to date and store
    if(annual_trend_n_samples > 0):
      annual_mean_to_date = annual_trend_total / annual_trend_n_samples
      write_json_file(
        {
          'year': today.year,
          'ppm': annual_mean_to_date,
        }, 
        os.path.join(os.getcwd(), api_version, str(today.year), 'index.json')
      )

    # Fill in recent months from estimated daily values
    daily = iterate_csv_rows(daily_data)
    last_row_ppm = {}
    for row in daily:
      # Only consider current and past year
      if int(row['year']) >= today.year-1:
        # This CSV has leading spaces on months. Remove them.
        month = row['month'].lstrip()
        # Check if this month folder exists
        path = os.path.join(os.getcwd(), api_version, row['year'], month, 'index.json')
        if os.path.exists(path):
          continue
        # Create monthly file from first day of the month
        last_row = float(row['trend'])
        write_json_file(
          {
            'year': int(row['year']),
            'month':int(month),
            'ppm': float(row['trend'])
          }, 
          path
        )

    # If there's no data for current month, copy the previous month's data
    path = os.path.join(os.getcwd(), api_version, str(today.year), str(today.month), 'index.json')
    if (os.path.exists(path) == False):
      write_json_file(
        {
          'year': today.year,
          'month': today.month,
          'ppm': last_row_ppm,
          'simulated': True,
        },
        path
      )
