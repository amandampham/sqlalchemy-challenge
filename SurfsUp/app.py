# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################


#Create Engine 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# Save references to each table
table_references = {}

measurement_class = Base.classes.measurement
station_class = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#Homepage and available routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )
#Participation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    most_recent_date = session.query(measurement_class.date).order_by(measurement_class.date.desc()).first()
    most_recent_date = most_recent_date[0]
    most_recent_date = dt.date.fromisoformat(most_recent_date)

    year_ago = most_recent_date - dt.timedelta(days= 365)
   
    # Perform the query and retrieve the last 12 months of precipitation data
    results = session.query(measurement_class.date, measurement_class.prcp).filter(measurement_class.date >= year_ago).all()
    
    # Convert query results to a dictionary
    precipitation_dictionary = []
    for date, prcp in results:
        temporary = {}
        temporary['date'] = date
        temporary['prcp'] = prcp
        precipitation_dictionary.append(temporary)
    
    # Return JSON representation of the dictionary
    return jsonify(precipitation_dictionary)


#Stations Route 
@app.route("/api/v1.0/stations")
def stations():
    # Query and retrieve the list of stations
    stations_query = session.query(station_class.name, station_class.station)
    stations = stations_query.all()

    # Convert results into a dictionary 
    station_dictionary = []
    for name, station in stations:
        temporary = {}
        temporary['name'] = name
        temporary['station'] = station
        station_dictionary.append(temporary)

    # Return a JSON list of stations
    return jsonify(station_dictionary)


#Temperature Observations Route
@app.route("/api/v1.0/tobs")
def tobs():
    # Query and retrieve the temperature observations of the most-active station for the previous year
   # Find the most active station
    active_station = session.query(measurement_class.station, func.count(measurement_class.station)).\
        group_by(measurement_class.station).\
        order_by(func.count(measurement_class.station).desc()).first()[0]
    
    most_recent_date = session.query(measurement_class.date).order_by(measurement_class.date.desc()).first()
    most_recent_date = most_recent_date[0]
    most_recent_date = dt.date.fromisoformat(most_recent_date)

    year_ago = most_recent_date - dt.timedelta(days= 365)
    
    # Query and retrieve the temperature observations of the most-active station for the previous year
    results = session.query(measurement_class.date, measurement_class.tobs).\
        filter(measurement_class.station == active_station).\
        filter(measurement_class.date >= year_ago).all()
    
    # Convert query results to a dictionary
    tobs_dictionary = []
    for date, tobs in results:
        temporary = {}
        temporary['date'] = date
        temporary['tobs'] = tobs
        tobs_dictionary.append(temporary)
    
    # Return a JSON list of temperature observations
    return jsonify(tobs_dictionary)

  
#Start and End Range Route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
 # Query and calculate the temperature statistics based on the start and end dates (if provided)
    if end:
        # Calculate the temperature statistics for the specified start-end range
        results = session.query(func.min(measurement_class.tobs), func.avg(measurement_class.tobs), func.max(measurement_class.tobs)).\
            filter(measurement_class.date >= start).filter(measurement_class.date <= end).all()
    else:
        # Calculate the temperature statistics from the specified start date till the last available date
        results = session.query(func.min(measurement_class.tobs), func.avg(measurement_class.tobs), func.max(measurement_class.tobs)).\
            filter(measurement_class.date >= start).all()

    # Convert query results to a dictionary
    temperature_stats_dictionary = []
    for Tmin, Tavg, Tmax in results:
        temporary = {}
        temporary['TMIN'] = Tmin
        temporary['TAVG'] = Tavg
        temporary['TMAX'] = Tmax
        temperature_stats_dictionary.append(temporary)

    # Return a JSON list of the temperature statistics
    return jsonify(temperature_stats_dictionary)




if __name__ == '__main__':
    app.run(debug=True)

