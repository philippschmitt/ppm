# ppm
A file-based API for historical atmospheric CO<sub>2</sub> concentrations.

Data comes from https://gml.noaa.gov/ccgg/trends/gl_data.html and includes monthly and annual data ranging from January 1979 to today (always a few months behind).

## How to use
The API is hosted on GitHub Pages and makes the following endpoints available:

### Globally averaged marine surface annual mean data
`https://philippschmitt.github.io/ppm/v1/{YYYY}`

### Globally averaged marine surface monthly trend data (de-seasonalized)
`https://philippschmitt.github.io/ppm/v1/{YYYY}/{M}`
