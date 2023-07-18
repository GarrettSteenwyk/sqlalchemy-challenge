# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

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
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

#precipitation query
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """listing precipitation and date"""
    results = session.query(measurement.date,measurement.prcp).all()

    session.close()
    
    
    all_precepitation=[]
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precepitation.append(precipitation_dict)

    return jsonify(all_precepitation)

#station query
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """listing all stations"""
    results = session.query(station.id, station.station, station.name,
                            station.latitude, station.longitude, station.elevation).all()
    
    session.close()
   
   
    all_station=[]
    for id,station,name,latitude,longitude,elevation in results:
        station_dict={}
        station_dict['Id']=id
        station_dict['station']=station
        station_dict['name']=name
        station_dict['latitude']=latitude
        station_dict['longitude']=longitude
        station_dict['elevation']=elevation
        all_station.append(station_dict)
    return jsonify(all_station)

#temp opbservations 
@app.route("/api/v1.0/tobs")
def tempartureobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all temparture observation"""
    results_date=session.query(measurement.date).order_by(measurement.date.desc()).first()
    str_date=list(np.ravel(results_date))[0]
    latest_date=dt.datetime.strptime(str_date,"%Y-%m-%d")
    year_back=latest_date-dt.timedelta(days=366)

    results=session.query(measurement.date, measurement.tobs).order_by(measurement.date.desc()).\
            filter(measurement.date>=year_back).all()
    
    session.close()
    
    
    temp_obs=[]
    for tobs,date in results:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['tobs']=tobs
        temp_obs.append(tobs_dict)
    return jsonify(temp_obs)

#temp observations but only the summary stat ones (start/end edition)
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    session.close()
    
    
    temp_range={}
    temp_range["Min_Temp"]=results[0][0]
    temp_range["avg_Temp"]=results[0][1]
    temp_range["max_Temp"]=results[0][2]
    return jsonify(temp_range)

#temp observations but only the summary stat ones (start only edition)
@app.route("/api/v1.0/<start>")
def calc_temps_sd(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
   
    results=session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                filter(measurement.date >= start).all()
    
    session.close()
    
    
    temp_start={}
    temp_start["Min_Temp"]=results[0][0]
    temp_start["avg_Temp"]=results[0][1]
    temp_start["max_Temp"]=results[0][2]
    return jsonify(temp_start)
if __name__ == '__main__':
    app.run(debug=True)