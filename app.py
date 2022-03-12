import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
session = Session(engine)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<center><h1>Welcome to the Home Page! :)</h1><br/>"
        f"<h3>Available Routes:</h3><br/>"
        f"Precipitation     |     /api/v1.0/precipitation<br/>"
        f"Stations     |     /api/v1.0/stations<br/>"
        f"TOBS for Prevous Year     |     /api/v1.0/tobs<br/>"
        f"Start Temp Calculations (Date Format yyyy-mm-dd)     |     /api/v1.0/&lt;start&gt;<br/>"
        f"Start to End Temp Calculations (Date Format yyyy-mm-dd)      |     /api/v1.0/&lt;start&gt;/&lt;end&gt;<br/></center>"
    )

#################################################
# Precipitation
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():

    #Last 12 months of precipitation data
    prcp_results = session.query(measurement.date,measurement.prcp).filter(measurement.date>'2016-08-22').order_by(measurement.date.desc()).all()
    
    session.close()

    #Convert query results to a dictionary
    all_dates = []
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict[date]= prcp
        all_dates.append(prcp_dict)

    #Return json 
    return (
        jsonify(all_dates)
    )


#################################################
# Stations
#################################################
@app.route("/api/v1.0/stations")
def stations():
    # Return query results
    station_results = session.query(station.name).all()

    session.close()

    all_stations = list(np.ravel(station_results))
    return jsonify(all_stations)

                        
#################################################
# Tobs
#################################################                        
@app.route("/api/v1.0/tobs")
def tobs():

    #Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #Query the primary station for all tobs from the last year
    results = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= prev_year).all()

    session.close()

    #Convert restults to a list
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps=temps)


#################################################
# Start
#################################################   
@app.route("/api/v1.0/<start>")
def date(start):
    
    temp_query_start = session.query(func.min(measurement.tobs).label("TMIN"),func.max(measurement.tobs).label("TMAX"),\
                    func.avg(measurement.tobs).label("TAVG")).filter(measurement.date>=start).all()


    all_temp_query = []
    
    for row in temp_query_start:
        row_dict = {}
        row_dict["Minimum Temperature"] = row.TMIN
        row_dict["Maximum Temperature"] = row.TMAX
        row_dict["Average Temperature"] = row.TAVG
        all_temp_query.append(row_dict)
    session.close()
    return jsonify(all_temp_query)



#################################################
# Start/End
#################################################
@app.route("/api/v1.0/<start>/<end>")
def date_range(start=None,end=None):
    start_dt=dt.datetime.strptime(start, '%d%m%Y')
    
    if not end:
        temp_query = session.query(func.min(measurement.tobs).label("TMIN"),func.max(measurement.tobs).label("TMAX"),\
                        func.avg(measurement.tobs).label("TAVG")).filter(measurement.date>=start).all()

    else:
        temp_query = session.query(func.min(measurement.tobs).label("TMIN"),func.max(measurement.tobs).label("TMAX"),\
                        func.avg(measurement.tobs).label("TAVG")).filter(measurement.date>=start).filter(measurement.date<=end).all()


    all_temp_query = []    
    for row in temp_query:
        row_dict = {}
        row_dict["Minimum Temperature"] = row.TMIN
        row_dict["Maximum Temperature"] = row.TMAX
        row_dict["Average Temperature"] = row.TAVG
        all_temp_query.append(row_dict)
    session.close()
    return jsonify(all_temp_query)




if __name__ == '__main__':
    app.run(debug=True)
