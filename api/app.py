import json
from datetime import timedelta, datetime

from flask import Flask
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

app = Flask(__name__)

engine = create_engine("sqlite:///../Resources/hawaii.sqlite", echo=True)
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
conn = engine.connect()
Measurement = Base.classes.measurement
Station = Base.classes.station


# 3. Define static routes
@app.route("/")
def index():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt start &gt<br/>"
        f"/api/v1.0/&lt start &gt/&lt end &gt<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    latest_row = session.query(Measurement).order_by(Measurement.date.desc()).first()
    latest_date = datetime.strptime(latest_row.date, '%Y-%m-%d')
    date_12_months_ago = latest_date.date() - timedelta(days=366)
    rows = session.query(Measurement).filter(Measurement.date > date_12_months_ago).all()
    result_dict = {}
    for row in rows:
        result_dict[row.date] = row.prcp

    return json.dumps(result_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    all_stations = session.query(Station).all()
    result_list = []
    for station in all_stations:
        result_list.append(station.name)

    return json.dumps(result_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    latest_row = session.query(Measurement).order_by(Measurement.date.desc()).first()
    latest_date = datetime.strptime(latest_row.date, '%Y-%m-%d')
    date_12_months_ago = latest_date.date() - timedelta(days=366)
    rows = session.query(Measurement).filter(Measurement.date > date_12_months_ago).all()
    result_tobs =[]
    for row in rows:
        result_tobs.append(row.tobs)

    return json.dumps(result_tobs)


@app.route("/api/v1.0/<start>")
def tobs_start(start):
    session = Session(engine)

    def calc_temps(trip_start_date):
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)). \
            filter(Measurement.date >= trip_start_date).first()

    data = calc_temps(start)
    return json.dumps({"min": data[0], "avg": data[1], "max": data[2]})


@app.route("/api/v1.0/<start>/<end>")
def tobs_end(start, end):
    session = Session(engine)
    data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)). \
            filter(Measurement.date.between(start, end)).first()
    return json.dumps({"min": data[0], "avg": data[1], "max": data[2]})


if __name__ == "__main__":
    app.run(debug=True)
