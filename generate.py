import urllib.request
import csv
import os
import shutil
import json
import datetime
from statistics import mean


def fetch_csv_from_web(url):
    try:
        # Fetch the data from the URL
        response = urllib.request.urlopen(url)
        data = response.read().decode("utf-8")
        return data
    except Exception as e:
        print("An error occurred:", e)
        return None


# Ignore comments in csv file
# Source: https://stackoverflow.com/questions/14158868/python-skip-comment-lines-marked-with-in-csv-dictreader
def decomment(csvfile):
    for row in csvfile:
        raw = row.split("#")[0].strip()
        if raw:
            yield raw


def iterate_csv_rows(csv_data):
    if csv_data is not None:
        csv_lines = csv_data.splitlines()
        csv_reader = csv.DictReader(decomment(csv_lines), skipinitialspace=True)
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
    # GET: philippschmitt.github.io/ppm/{api_version}/{YYYY}/{M}
    api_version = "v1"

    # Fetched data
    annual_data = fetch_csv_from_web(annual_csv_url)
    monthly_data = fetch_csv_from_web(monthly_csv_url)
    daily_data = fetch_csv_from_web(daily_csv_url)
    # Computed data
    year_to_date_data = []
    monthly_data_computed = {}

    # Delete API folder if it already exists from previous build
    shutil.rmtree(os.path.join(os.getcwd(), api_version), ignore_errors=True)

    latest_annual_data_date = None
    latest_monthly_data_date = None
    today = datetime.datetime.combine(
        datetime.date.today(), datetime.datetime.min.time()
    )

    # Get annual mean atmospheric carbon and store in year folders
    for row in iterate_csv_rows(annual_data):
        write_json_file(
            {
                "year": int(row["year"]),
                "ppm": float(row["mean"]),
            },
            os.path.join(os.getcwd(), api_version, row["year"], "index.json"),
        )
        # Update latest annual data record
        latest_annual_data_date = datetime.datetime(int(row["year"]), 1, 1)

    # Get monthly atmospheric carbon and store in month folders
    for row in iterate_csv_rows(monthly_data):
        write_json_file(
            {
                "year": int(row["year"]),
                "month": int(row["month"]),
                "ppm": float(row["trend"]),
            },
            os.path.join(
                os.getcwd(), api_version, row["year"], row["month"], "index.json"
            ),
        )
        # Update latest monthly data record
        latest_monthly_data_date = datetime.datetime(
            int(row["year"]), int(row["month"]), 1
        )

    # Create data structure for back-filling data
    current_date = latest_monthly_data_date.replace(
        month=latest_monthly_data_date.month + 1
    )
    while current_date <= today:
        # Add empty dict
        if current_date.year not in monthly_data_computed:
            monthly_data_computed[current_date.year] = {}
        if current_date.month not in monthly_data_computed[current_date.year]:
            monthly_data_computed[current_date.year][current_date.month] = []
        # Increment to the next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

    # Populate recent months from estimated daily values
    for row in iterate_csv_rows(daily_data):
        # For efficiency, only consider current and past year
        if int(row["year"]) < today.year - 1:
            continue
        # Add current year data to year-to-date
        if int(row["year"]) > latest_annual_data_date.year:
            year_to_date_data.append(float(row["trend"]))
        # Store monthly data
        if float(row["year"]) in monthly_data_computed:
            if float(row["month"]) in monthly_data_computed[float(row["year"])]:
                monthly_data_computed[float(row["year"])][float(row["month"])].append(
                    float(row["trend"])
                )

    # Write computed monthly data
    last_month_data = 0
    for year in monthly_data_computed:
        for month in monthly_data_computed[year]:
            daily_values = monthly_data_computed[year][month]
            # If there is no daily data for the current month use last
            # month's data until we have data available.
            if len(daily_values) == 0:
                data = last_month_data
            else:
                data = mean(daily_values)
            write_json_file(
                {
                    "year": year,
                    "month": month,
                    "ppm": data,
                },
                os.path.join(
                    os.getcwd(), api_version, str(year), str(month), "index.json"
                ),
            )
            last_month_data = data

    # Write year-to-date as annual value
    write_json_file(
        {
            "year": today.year,
            "ppm": mean(year_to_date_data),
        },
        os.path.join(os.getcwd(), api_version, row["year"], "index.json"),
    )
