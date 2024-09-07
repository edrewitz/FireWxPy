# This script simulates downloading data inside of the function
# Imports the needed modules and functions
from firewxpy import nws_relative_humidity_forecast, nws_temperature_forecast

# Makes the graphics for the state of Maine
nws_temperature_forecast.plot_extreme_heat_forecast(temp_scale_warm_start=80, temp_scale_warm_stop=100, state='me')
nws_temperature_forecast.plot_extremely_warm_low_temperature_forecast(temp_scale_warm_start=60, temp_scale_warm_stop=80, state='me')
nws_temperature_forecast.plot_frost_freeze_forecast(state='me')
nws_temperature_forecast.plot_maximum_temperature_forecast(state='me')
nws_temperature_forecast.plot_maximum_temperature_trend_forecast(state='me')
nws_temperature_forecast.plot_minimum_temperature_forecast(state='me')
nws_temperature_forecast.plot_minimum_temperature_trend_forecast(state='me')

nws_relative_humidity_forecast.plot_excellent_overnight_recovery_relative_humidity_forecast(state='me')
nws_relative_humidity_forecast.plot_low_minimum_relative_humidity_forecast(low_minimum_rh_threshold=60, state='me')
nws_relative_humidity_forecast.plot_maximum_relative_humidity_forecast(state='me')
nws_relative_humidity_forecast.plot_maximum_relative_humidity_trend_forecast(state='me')
nws_relative_humidity_forecast.plot_minimum_relative_humidity_forecast(state='me')
nws_relative_humidity_forecast.plot_minimum_relative_humidity_trend_forecast(state='me')
nws_relative_humidity_forecast.plot_poor_overnight_recovery_relative_humidity_forecast(poor_overnight_recovery_rh_threshold=70, state='me')
