# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
print(Base.classes.keys())

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation data for the last year"""
    # Query the most recent date
    recent_date = session.query(func.max(Measurement.date)).first()[0]
    one_year_ago = (dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the last year of the most active station"""
    # Query the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Query the most recent date and calculate one year ago
    recent_date = session.query(func.max(Measurement.date)).first()[0]
    one_year_ago = (dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query temperature observations for the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Convert the query results to a list of dictionaries
    tobs_data = [{"date": date, "temperature": tobs} for date, tobs in results]

    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>")
def start(start):
    """Return min, avg, and max temperature from the start date to the end of the dataset"""
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    session.close()

    # Convert the query results to a dictionary
    temperature_data = {
        "Start Date": start,
        "Min Temp": results[0][0],
        "Avg Temp": results[0][1],
        "Max Temp": results[0][2]
    }

    return jsonify(temperature_data)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return min, avg, and max temperature for a specific date range"""
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Convert the query results to a dictionary
    temperature_data = {
        "Start Date": start,
        "End Date": end,
        "Min Temp": results[0][0],
        "Avg Temp": results[0][1],
        "Max Temp": results[0][2]
    }

    return jsonify(temperature_data)


if __name__ == '__main__':
    app.run(debug=True)