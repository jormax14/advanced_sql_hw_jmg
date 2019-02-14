import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

#reflect an existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(engine, reflect = True)

#save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create our session (link) from Python to the db
session = Session(engine)


#flask setup
app = Flask(__name__)

#flask routes
@app.route('/')
def welcome():
    """list all available api routes."""
    return (
        f'available routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<start><br/>'
        f'/api/v1.0/<start>/<end>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    """returns precipitation dictionary from last year"""
    #setup query to return last date of data available
    precip_dates = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #calculate the date 1 year ago from the last data point in the database
    year_end = precip_dates[0]
    year_beg = dt.datetime.strptime(year_end, '%Y-%m-%d') - dt.timedelta(days = 366)
    #setup query to retrieve the dates and precipitation scores
    precip_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_beg).all()
    #convert query results into dictionary
    precip_dict = dict(precip_query)
    
    return jsonify(precip_dict)

@app.route('/api/v1.0/stations')
def stations():
    """returns list of stations"""
    #setup query of stations
    stations_query = session.query(Station.station).group_by(Station.station).all()
    #convert query results into list
    stations_list =list(np.ravel(stations_query))

    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def temperature():
    """returns temperatures from last year"""
    #setup query to return last date of data available
    temp_dates = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #calculate the date 1 year ago from the last data point in the database
    year_end = temp_dates[0]
    year_beg = dt.datetime.strptime(year_end, '%Y-%m-%d') - dt.timedelta(days = 366)
    #setup query to retrieve the dates and temperature observations
    temp_query = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_beg).all()
    #coverty query results into list
    temp_list = list(temp_query)

    return jsonify(temp_list)

@app.route('/api/v1.0/<start>')
def start(start = None):
    """returns min, avg, and max temps for a given start date"""
    #setup query to return temp info after specified date
    start_query = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    #convert query results into list
    start_list = list(start_query)

    return jsonify(start_list)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start = None, end = None):
    """returnes min, avg, and max temps for define time period"""
    #setup query to return temp info for specified time period
    period_query = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    #convert query results into list
    period_list = list(period_query)
    return jsonify(period_list)


if __name__ == '__main__':
    app.run(debug=True)