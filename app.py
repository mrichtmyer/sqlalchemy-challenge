# imports
from flask import Flask, jsonify
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

import numpy as np
import pandas as pd

# global functions
def connectToSQL():
        engine = create_engine("sqlite:///Resources/hawaii.sqlite")
        conn = engine.connect()

        # reflect an existing database into a new model
        Base = automap_base()
        # reflect the tables
        Base.prepare(engine, reflect=True)
        # Save references to each table
        Measurement = Base.classes.measurement
        Station = Base.classes.station

        # Create our session (link) from Python to the DB
        session = Session(engine)

        return Measurement, Station, session, conn




# Create an app, being sure to pass __name__
app = Flask(__name__)


# Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (f"Welcome to my 'Home' page!<br>"
            f"All routes possible:<br>"
            f"/api/v1.0/precipitation<br>"
            f"/api/v1.0/stations<br>"
            f"/api/v1.0/<start><br>"
            f"/api/v1.0/<start>/<end>")


# precipitation route - provide information about the date and precipitations
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitaion' page...")
    return "Precipitation"




# precipitation route - provide information about the date and precipitations
@app.route("/api/v1.0/stations")
def station():
    print("Server received request for 'Stations' page...")

    # connect to database and retrieve tables, session and connection
    Measurement, Station, session, conn = connectToSQL()

    # parse through all distinct stations in database and store in list
    station_list = []
    for value in session.query(Station.station).distinct():
        station_list.append(value)
    # return jsonified list of all stations
    return jsonify(station_list)





#### Query dates and temperatures within a year from last data point
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")


    Measurement, Station, session, conn = connectToSQL()

    # pull all data into DataFrame so we can quickly calculate the max date
    data = pd.read_sql("SELECT * FROM measurement", conn)
    max_date = data["date"].max()

    # use dt.datetime.timedelta to calculate the date 1 year previous (i.e. 52 weeks before)
    one_year_ago = dt.datetime.strptime(max_date, '%Y-%m-%d')-dt.timedelta(weeks=52)

    # convert back into same format this database is using: YYYY-MM-DD
    one_year_ago = one_year_ago.strftime("%Y-%m-%d")

    # perform query
    prcp_1yr = session.query(Measurement).filter(Measurement.date < max_date, Measurement.date > one_year_ago)

    # preallocate lists
    date, tobs = [],[]

    for row in prcp_1yr:
        # store all data in lists - to be combined in dataframe next
        date.append(row.date)
        tobs.append(row.tobs)

    df = pd.DataFrame({"Date": date, "Tobs": tobs})
    import json
    return jsonify(json.loads(df.to_json(orient="records")))

#### MAKE API CALLS FOR TEMP STATISTICS WITHIN DATE RANGES ####
# precipitation route - provide information about the date and precipitations
@app.route("/api/v1.0/<start>")
def start_query(start):
    print("Server received request for 'Start' page...")
    return jsonify(start)


if __name__ == "__main__":
    app.run(debug=True)
