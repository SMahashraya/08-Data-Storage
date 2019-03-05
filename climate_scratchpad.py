# Import dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc

import pandas as pd

import datetime as dt
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify

## Set up engine function
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Design a query to retrieve the last 12 months of precipitation data and plot the results
# Calculate the date 1 year ago from the last data point in the database
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
year_ago = dt.date(2017, 8, 23) - relativedelta(months=12)
print(year_ago)

# Perform a query to retrieve the data and precipitation scores
prcp_to_year = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago).\
    order_by(Measurement.date).all()
prcp_to_year

# Design a query to show how many stations are available in this dataset
stations = session.query(Measurement.station).\
    group_by(Measurement.station).count()
print(stations)

# What are the most active stations? (i.e. what stations have the most rows)?
most_active = session.query(func.count(Measurement.date).\
                                label("count"), Measurement.station ).\
                                group_by(Measurement.station).\
                                order_by(desc("count")).limit(4).all()
most_active
# List the stations and the counts in descending order.
all_stations = session.query(Measurement.station, func.count(Measurement.date).\
                                label("count")).\
                                group_by(Measurement.station).\
                                order_by(desc("count")).all()
all_stations

# Using the station id from the previous query, calculate the lowest temperature recorded, 
# highest temperature recorded, and average temperature most active station?
hottest = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs), Measurement.station).\
                        filter(Measurement.station == "USC00519281").\
                        order_by(Measurement.station).all()
hottest

# Choose the station with the highest number of temperature observations.
# Query the last 12 months of temperature observation data for this station
active_twelve = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
    filter(Measurement.date >= year_ago, Measurement.station == "USC00519281").\
    order_by(Measurement.station).all()
# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVG, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

def calc_temps1(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVG, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

# function usage example
print(calc_temps('2012-02-28', '2012-03-05'))

# function usage example
print(calc_temps('2012-02-28', '2012-03-05'))

# Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax
# for your trip using the previous year's data for those same dates.
last_year = calc_temps("2016-08-23", "2017-08-23")
print(last_year)

# Calculate the rainfall per weather station for your trip dates using the previous year's matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation
measure_station_join = session.query(Measurement.date,
                                     Measurement.station,
                                     func.sum(Measurement.prcp).\
                                     label("sum"),
                                     Station.name,
                                     Station.latitude, 
                                     Station.longitude,  
                                     Station.elevation).\
    filter(Measurement.station == Station.station,
           Measurement.date >= year_ago).\
    group_by(Measurement.station).\
    order_by(desc("sum")).all()


# Create a query that will calculate the daily normals 
# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)

def daily_normals(date):
    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    
daily_normals("02-01")

# calculate the daily normals for your trip
# push each tuple of calculations into a list called `normals`

# Set the start and end date of the trip
# Use the start and end date to create a range of dates
# Stip off the year and save a list of %m-%d strings
trip_dates = [d.strftime("%m-%d") for d in pd.date_range("08-01-2016","08-08-2016")]

# Loop through the list of %m-%d strings and calculate the normals for each date
normals = []
for d in trip_dates:
    normals.append(daily_normals(d))
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp_data = []
    
    for prcp_element in prcp_to_year:
        prcp_dict = {}
        prcp_dict["Date"] = prcp_element.date
        prcp_dict["Precipitation"] = prcp_element.prcp
        prcp_data.append(prcp_dict)
        
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    stations_data = []
    
    for element in measure_station_join:
        stations_dict = {}
        stations_dict["Date"] = measure_station_join.date
        stations_dict["Station"] = measure_station_join.station
        stations_dict["Station Name"] = measure_station_join.name
        stations_dict["Latitude"] = measure_station_join.latitude
        stations_dict["Longitude"] = measure_station_join.longitude
        stations_dict["Elevation"] = measure_station_join.elevation
        stations_data.append(stations_dict)
        
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    tobs_data = []
    
    for tobs_element in active_twelve:
        tobs_dict = {}
        tobs_dict["Date"] = active_twelve.date
        tobs_dict["Station"] = active_twelve.station
        tobs_dict["Temperature"] = active_twelve.tobs
        tobs_data.append(tobs_dict)
        
    return jsonify(tobs)


@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Precipitation API!<br/>"
        f"Available Routes:<br/>"
        "Precipitation Over Past 12 Months"
        f"/api/v1.0/precipitation<br/>"
        "All Stations"
        f"/api/v1.0/stations<br/>"
        "Temperature Observations Over Past 12 Months"
        f"/api/v1.0/tobs<br/>"
    )

@app.route("/api/v1.0/<start>")
def start_date():
    start_temp = []
    
    for TMin, TAvg, TMax in calc_temps1:
        start_temp_dict = {}
        start_temp_dict["Minimum Temperature"] = TMin
        start_temp_dict["Average Temperature"] = TAvg
        start_temp_dict["Maximum Temperature"] = TMax
        start_temp.append(start_temp_dict)
        
    return jsonify(start_date)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date():
    start_temp = []
    
    for TMin, TAvg, TMax in calc_temps:
        start_temp_dict = {}
        start_temp_dict["Minimum Temperature"] = TMin
        start_temp_dict["Average Temperature"] = TAvg
        start_temp_dict["Maximum Temperature"] = TMax
        start_temp.append(start_temp_dict)
        
    return jsonify(start_end_date)

if __name__ == "__main__":
    app.run(debug=True)