# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, DateTime

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# the welcome page
@app.route("/")
def welcome():
    #list all available routes
    return(
    f"Available Routes:<br/>"
    f"<br/>"
    f"All Dates with Precipitation<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"<br/>"
    f"Station List<br/>"
    f"/api/v1.0/stations<br/>"
    f"<br/>"
    f"Temperature Observed for Most Active Station<br/>"
    f"/api/v1.0/tobs<br/>"
    f"<br/>"
    f"Retrieve min temp, max temp, and avg temp for all dates after your specified start date<br/>"
    f"/api/v1.0/yyyy-mm-dd<br/>"
    f"<br/>"
    f"Retrieve min temp, max temp, and avg temp for all dates between your specified start and end dates<br/>"
    f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"

    )

########################
# Precipitation Route
########################

@app.route("/api/v1.0/precipitation")
def precipitation():
    

        # Find the most recent date in the data set.
    last_row = session.query(measurement).order_by(measurement.date.desc()).first()

    last_date = last_row.__dict__['date']
    last_year_date = (dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days = 365)).strftime("%Y-%m-%d") # reconverts the whole string conversion back to formatted datetime

    # Perform a query to retrieve the data and precipitation scores
    precip_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= last_year_date).all()

    session.close()
    # Create a dictionary to store data
    date_precip = []
    for day, precip in precip_data:
        precip_dict = {}
        precip_dict['day'] = day
        precip_dict['prcp'] = precip
        date_precip.append(precip_dict)

    return jsonify(date_precip)


########################
# Stations Route
########################
@app.route("/api/v1.0/stations")
def stations():
     
    station_list = session.query(station.station).all()
    session.close()

    # to return a list of things in JSON format, use list(np.ravel)
    all_stations = list(np.ravel(station_list))

    return jsonify(all_stations)


########################
# Temperature Observed Route
########################
@app.route("/api/v1.0/tobs")
def tobs():
    # most active station would be the [0][0] of this query
    most_active = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active_last_date = session.query(measurement).filter(measurement.station == most_active[0][0]).order_by(measurement.date.desc()).first().__dict__['date']


    # find 1 year prior
    # strptime = string parse time -> converts string to datetime
    # strftime = string format time -> converts datetime to string
    most_active_one_year_ago = (dt.datetime.strptime(most_active_last_date, "%Y-%m-%d") - dt.timedelta(days = 365)).strftime("%Y-%m-%d")

    # collect the previous one year's data
    most_active_last_year_data = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= most_active_one_year_ago).\
        filter(measurement.station == most_active[0][0]).all()
    most_active_last_year_data

    session.close()

    # convert into list
    most_active_station_data = list(np.ravel(most_active_last_year_data))

    return jsonify(most_active_station_data)

########################
# Start Route
########################

@app.route("/api/v1.0/<start>")
def date_start(start):


    start_date = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).group_by(measurement.date).all()

    session.close()

    temp_list = []
    for date, min, avg, max in start_date:
        start_temp_dict = {}
        start_temp_dict['date'] = date
        start_temp_dict['min temp'] = min
        start_temp_dict['avg temp'] = avg
        start_temp_dict['max temp'] = max
        temp_list.append(start_temp_dict)


    return jsonify(temp_list)

########################
# Start/END Route
########################

@app.route("/api/v1.0/<start>/<end>")
def date_range(start,end):

    range_dates = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start, measurement.date <= end).group_by(measurement.date).all()
    
    session.close()
    
    range_temp_list = []
    for date, min, avg, max in range_dates:
        range_temp_dict = {}
        range_temp_dict['date'] = date
        range_temp_dict['min temp'] = min
        range_temp_dict['avg temp'] = avg
        range_temp_dict['max temp'] = max
        range_temp_list.append(range_temp_dict)


    return jsonify(range_temp_list)


if __name__ == '__main__':
    app.run(debug=True)