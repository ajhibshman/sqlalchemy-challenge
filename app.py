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
        f"/api/v1.0/start_date/end_date<br/>"
        f"    Enter dates in year-month-date format<br/>"
        f"/api/v1.0/start_date<br/>"
        f"    Enter date in yyyy-mm-dd format<br/>"  
        f"date range from Jan 1 2010 to Aug 23 2017" 
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

#4) Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a 
# given start or start-end range.

#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start_date>")
def start_temps(start_date):
    session=Session(engine)

    result5=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    session.close()

    start_temp_data = []
    for min, avg, max in result5:
        start_temp_dict = {}
        start_temp_dict["Minimum"] = min
        start_temp_dict["Average"] = avg
        start_temp_dict["Maximum"] = max
        start_temp_data.append(start_temp_dict)

    return jsonify(start_temp_data)


# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    session = Session(engine)

    result4=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    session.close()

    temp_data = []
    for min, avg, max in result4:
        temp_dict = {}
        temp_dict["Minimum"] = min
        temp_dict["Average"] = avg
        temp_dict["Maximum"] = max
        temp_data.append(temp_dict)

    return jsonify(temp_data)


if __name__ == '__main__':
    app.run(debug=True)







