# ppm
A file-based API for historical atmospheric CO<sub>2</sub> concentrations. 

The API returns mean, de-seasonalized trend data from [NOAA Trends in Atmospheric Carbon Dioxide](https://gml.noaa.gov/ccgg/trends/gl_data.html), which includes monthly and annual data ranging from January 1979 to today (always a few months behind). Recent months for which there are no estimates are approximated from NOAA's daily estimates.

## How to use
The API is hosted on GitHub Pages and makes the following endpoints available:

### Globally averaged marine surface annual mean data
`https://philippschmitt.github.io/ppm/v1/{YYYY}`

NOAA data does not include the annual mean for the current year (obviously...). For the current year, the API returns the mean of the monthly trend data available-to-date.

### Globally averaged marine surface monthly trend data (de-seasonalized)
`https://philippschmitt.github.io/ppm/v1/{YYYY}/{m}`

NOAA data is a few months behind (three, at time of writing). Missing months are filled in with data from the [Estimated Global Trend daily values](https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_trend_gl.csv) dataset. Each month uses the first available row, i.e. first day of the month.
