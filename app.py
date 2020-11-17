# import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime

engine = create_engine("sqlite:///Resources/hawaii.sqlite",echo=False)

#reflect database
Base = automap_base()
Base.prepare(engine, reflect=True)

Station=Base.classes.station
Measurement=Base.classes.measurement

#flask routes
app=Flask(__name__)

#Index page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

# 1) precipitation query
@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """daily precipitation for last year of data all stations"""
    # Query last 12 months of precipitation data
    #get last date in table
    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #parse out date from result
    last_date1=last_date[0]
    #convert string to datetime
    last_date_conv = datetime.strptime(last_date1, '%Y-%m-%d')
    #subtract 1 year from last date  
    query_date = (last_date_conv) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    result=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= query_date).\
        order_by(Measurement.date).all()    

    session.close()

    # Create a dictionary from the row data and append to a list 
    precip_data = []
    for date, precp in result:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = precp
        precip_data.append(precip_dict)

    return jsonify(precip_data)

# 2) Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """list of stations submitting weather information"""
    #query and save db
    result2=session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()

    session.close()

    # Create a dictionary from the row data and append to a list 
    station_data = []
    for st,name,lat,long,elev in result2:
        station_dict = {}
        station_dict["Station"] = st
        station_dict["Name"] = name
        station_dict["Latitude"] = lat
        station_dict["Longitude"] = long
        station_dict["Elevation"] = elev
        station_data.append(station_dict)

    return jsonify(station_data)

# 3) Query the dates and temperature observations of the most active station for the last year of data.
#    Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """temperature observations for most active station last year of data"""

    #find most active station
    most_active=session.query(Measurement.station).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()
    most_active=most_active[0]

    #get query date for last year of data
    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date1=last_date[0]
    last_date_conv = datetime.strptime(last_date1, '%Y-%m-%d')
    query_date = (last_date_conv) - dt.timedelta(days=365)

    #query date and temp for last year of data filtering for most active station
    result3=session.query(Measurement.date,Measurement.tobs).filter(Measurement.station==most_active).\
        filter(Measurement.date >= query_date).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    tobs_data = []
    for date, tobs in result3:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)


if __name__ == '__main__':
    app.run(debug=True)







