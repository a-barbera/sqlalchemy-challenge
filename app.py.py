#Flask webpage building for Module 10 challenge

# 1. Import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify
# from flask_sqlalchemy import SQLAlchemy


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



# 2. Create an app
app = Flask(__name__)

#####################################################

# Use Flask to create your routes, as follows:

####################################################

#     * Homepage.
#     * List all available routes.

@app.route("/")
def index():
    return (
        f"Welcome to the landing page for Anna's Hawaii Vacation Weather App!<br/>"
        f"<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f'/api/v1.0/stations<br/>'
        f"/api/v1.0/tobs<br/>"
        f"<br/><br/>"
        f'Choose a date or date range below:<br/>'
        f"<br/><br/>"
        f'When choosing a date, please use this format to ensure best results: <br/> YYYY-MM-DD<br/>'
        f"<br/><br/>"
        f'/api/v1.0/start_date/&lt;start_date&gt;<br/>'
        f'/api/v1.0/range/&lt;start_date&gt;/&lt;end_date&gt;<br/>'
    )

####################################################

# * `/api/v1.0/precipitation`
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create session link
    session = Session(engine)

    #Query measurements

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date.date
    latest_date = datetime.strptime(last_date, '%Y-%m-%d')
    year_ago = latest_date - relativedelta(years=1)
    latest_year = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= year_ago).all()

    #close session:
    session.close()
    
# * Convert the query results to a dictionary using `date` as the key and `prcp` as the value. 
    # Convert into a dictionary:
    date_dict = []

    for date,prcp in latest_year:
        measurements_dict = {date:prcp}
        date_dict.append(measurements_dict)


  # * Return the JSON representation of your dictionary.
    return jsonify(date_dict)


####################################################

# * `/api/v1.0/stations`

#     * Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    #Create session link
    session = Session(engine)

    #Query stations
    results = session.query(Station.station).all()
    #close session:
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

####################################################

# * `/api/v1.0/tobs`

@app.route("/api/v1.0/tobs")
def tobs():

    #Create session link
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date.date
    latest_date = datetime.strptime(last_date, '%Y-%m-%d')
    year_ago = latest_date - relativedelta(years=1)
    latest_year = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= year_ago).all()


#     * Query the dates and temperature observations of the most active station for the previous year of data.
    results = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date.between('2016-08-23', '2017-08-23'))

    #close session
    session.close()

    # Create a dictionary from the row data and append to a list
    tobs_specific = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_specific.append(tobs_dict)


#     * Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_specific)


####################################################
# * `/api/v1.0/<start>` 

@app.route("/api/v1.0/start_date/<start_date>")
def start(start_date):
    #Create session link
    session = Session(engine)

#     * Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.

#     * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than or equal to the start date.

    temp_list = []

    max_temp = session.query(Measurement.date, func.max(Measurement.tobs)).filter(Measurement.date >= start_date)

    for date, tobs in max_temp:
        max_dict = {}
        max_dict['date'] = date
        max_dict['Max Temp:'] = tobs
        temp_list.append(max_dict)

    avg_temp = session.query(Measurement.date, func.round(func.avg(Measurement.tobs),2)).filter(Measurement.date >= start_date) 
    
    for date, tobs in avg_temp:
        avg_dict = {}
        avg_dict['date'] = date
        avg_dict['Average Temp:'] = tobs
        temp_list.append(avg_dict)

    min_temp = session.query(Measurement.date, func.min(Measurement.tobs)).filter(Measurement.date >= start_date)

    for date, tobs in min_temp:
        min_dict = {}
        min_dict['date'] = date
        min_dict['Min Temp:'] = tobs
        temp_list.append(min_dict)

    session.close()

    return jsonify(temp_list)
    
####################################################
# `/api/v1.0/<start>/<end>`

#     * Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.

#     * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than or equal to the start date.

#     * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates from the start date through the end date (inclusive).

@app.route("/api/v1.0/range/<start_date>/<end_date>")
def range(start_date,end_date):

        #Create session link
    session = Session(engine)

    temp_list = []

    max_temp = session.query(Measurement.date, func.max(Measurement.tobs)).filter(Measurement.date >= start_date)\
        .filter(Measurement.date <= end_date)

    for date, tobs in max_temp:
        max_dict = {}
        max_dict['date'] = date
        max_dict['Max Temp:'] = tobs
        temp_list.append(max_dict)

    avg_temp = session.query(Measurement.date, func.round(func.avg(Measurement.tobs),2)).filter(Measurement.date >= start_date)\
        .filter(Measurement.date <= end_date)
    
    for date, tobs in avg_temp:
        avg_dict = {}
        avg_dict['date'] = date
        avg_dict['Average Temp:'] = tobs
        temp_list.append(avg_dict)

    min_temp = session.query(Measurement.date, func.min(Measurement.tobs)).filter(Measurement.date >= start_date)\
        .filter(Measurement.date <= end_date)

    for date, tobs in min_temp:
        min_dict = {}
        min_dict['date'] = date
        min_dict['Min Temp:'] = tobs
        temp_list.append(min_dict)

    session.close()

    return jsonify(temp_list)
    

# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)







