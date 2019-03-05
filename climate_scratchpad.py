# Import dependencies
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc
from flask import Flask, jsonify

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
    
    for station_element in measurement_station_join:
        stations_dict = {}
        stations_dict["Date"] = measurement_station_join.date
        stations_dict["Station"] = measurement_station_join.station
        stations_dict["Station Name"] = measurement_station_join.name
        stations_dict["Latitude"] = measurement_station_join.latitude
        stations_dict["Longitude"] = measurement_station_join.longitude
        stations_dict["Elevation"] = measurement_station_join.elevation
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

# if __name__ == "__main__":
#     app.run(debug=True)