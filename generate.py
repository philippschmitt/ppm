import urllib.request
import csv
import os
import shutil
import json

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

def iterate_csv_rows(csv_data, iterator):
    if csv_data is not None:
        csv_lines = csv_data.splitlines()
        csv_reader = csv.DictReader(decomment(csv_lines))
        for row in csv_reader:
            iterator(row)
    else:
        print("CSV data is not available.")


def write_json_file(dict, filename):
  # Data to be written
  # with open(file, "w") as outfile:
  #   json.dump(dict, outfile)
  os.makedirs(os.path.dirname(filename))
  with open(filename, "w") as f:
    json.dump(dict, f)



if __name__ == "__main__":

    # Data Source: https://gml.noaa.gov/ccgg/trends/gl_data.html
    annual_csv_url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_gl.csv"
    monthly_csv_url = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.csv"

    # API Version 1
    # GET: philippschmitt.github.io/ppm/{YYYY}/{M}
    api_version = "v1"

    # Fetch data
    annual_data = fetch_csv_from_web(annual_csv_url)
    monthly_data = fetch_csv_from_web(monthly_csv_url)

    # Delete API folder if it already exists (i.e. previous build)
    shutil.rmtree(os.path.join(os.getcwd(), api_version), ignore_errors=True)

    # Get annual avg. atmospheric carbon and store in year folders
    iterate_csv_rows(annual_data, lambda row:
      write_json_file(
        {
          'ppm': row['mean'],
          'year': row['year'],
        }, 
        os.path.join(os.getcwd(), api_version, row['year'], 'index.json')
      )
    )


    # Get monthly atmospheric carbon and store in month folders
    iterate_csv_rows(monthly_data, lambda row:
      write_json_file(
        # Create output dictionary
        {
          'year': row['year'],
          # Change month pattern to matter JavaScript: 0 for January, 11 for Dec
          'month': int(row['month']) - 1,
          'ppm': row['trend'],
        }, 
        # Create output path
        os.path.join(os.getcwd(), api_version, row['year'], str(int(row['month'])-1), 'index.json')
      )
    )
