# Import necessary dependencies

import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify

# Setup database
# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect database
Base = automap_base()

# reflect tables
Base.prepare(engine, reflect=True)

# Save table references
Measurement = Base.classes.measurement
Station = Base.classes.station

# Setup Flash
app = Flask(__name__)


#Create a function that gets minimum, average, and maximum temperatures for a range of dates
# This function called "calc_temps" will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date,session):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


#Set Flask Routes
# Define and list ALL available routes

@app.route("/")
def main():
    """List all available API routes"""
    return(
        f"Available Routes: <br/>"
        f"(1)Precipitation ---> /api/v1.0/precipitation<br/>"
        f"(2)Stations ---> /api/v1.0/stations<br/>"
        f"(3)TOBS ---> /api/v1.0/tobs<br/>"
        f"(4)Start Date Only ---> /api/v1.0/<start><br/>"
        f"(5)Start and End Date ---> /api/v1.0/<start>/<end><br/>"
    )

# Create precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session link from python to the db
    session = Session(engine)
    # Create query
    results = session.query(Measurement.date, Measurement.prcp).all()
    # Close session
    session.close()

    precipitation_list = []
    for date, prcp in results:
        rain_dict = {}
        rain_dict['Date'] = date
        rain_dict['Precipitation'] = prcp
        precipitation_list.append(rain_dict)
    
    return jsonify(precipitation_list)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()

    station_list = []
    for station, name in results:
        station_dict = {}
        station_dict['Station'] = station
        station_dict['Name'] = name
        station_list.append(station_dict)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date >= query_date).all()
    session.close()

    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['Date'] = date
        tobs_dict['tobs'] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum, average, and maximum temperatures from the start date until
    the end of the database."""

    # create session
    session = Session(engine)

    #First we find the last date in the database
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date = final_date_query[0][0]

    #get the temperatures
    temps = calc_temps(start, max_date,session)

    #create a list
    return_list = []
    date_dict = {'start_date': start, 'end_date': max_date}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list of the minimum, average, and maximum temperatures from the start date unitl
    the end date."""

    # create session
    session = Session(engine)

    #get the temperatures
    temps = calc_temps(start, end,session)

    #create a list
    return_list = []
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    return jsonify(return_list)


if __name__ == "__main__":
    app.run(debug=True)
