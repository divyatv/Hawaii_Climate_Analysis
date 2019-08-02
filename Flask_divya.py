## ---------------------------------------------------------------------
# 1. Import Flask
from flask import Flask,jsonify

## import packages for sql queries and etc.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import SingletonThreadPool
####-------------------------------------------------------------------------
### Create an engine to connect to the database.
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
## -----------------------------------------------------------------------------------
###- open a session to the database.
session = Session(engine)

##### --------------------------------------------------------------------------------
# 2. Create an app
app = Flask(__name__)

### -----------------------------------------------------------------------------------
# 3. Define static routes
@app.route("/")
def index():
    return '''<strong>Are you going to Hawaii???<br>Check out the weather analysis before you board that flight. Click on the links to explore:</strong> <br> \
    
    <strong> \
    <a href="http://127.0.0.1:5000/api/v1.0/precipitation" target="_blank">1. /api/v1.0/precipitation</a><br> \
    <a href="http://127.0.0.1:5000/api/v1.0/stations" target="_blank">2. /api/v1.0/stations</a><br> \
    <a href="http://127.0.0.1:5000/api/v1.0/tobs " target="_blank">3. /api/v1.0/tobs</a><br>\
    </strong>\
    <br>\
    <img src="https://www.hawaiinewsnow.com/resizer/qRDoOlfikOQD-As0qViLpfliS4w=/1200x600/arc-anglerfish-arc2-prod-raycom.s3.amazonaws.com/public/BHV2ZWBW6BDJVFY3P3EPCDMS34.jpg">
    
    '''

## -------------------------------------------------------------------------------------------
@app.route("/api/v1.0/precipitation")
def cal_prcp():
    getdata= session.query(Measurement.prcp, Measurement.date).all()
    summary_dict={}
    for row in getdata:
        summary_dict[row[1]]=row[0]
    return jsonify(summary_dict)
## -------------------------------------------------------------------------------------------------
@app.route("/api/v1.0/stations")
def station_details():
    station_names=session.query(Measurement.station).group_by(Measurement.station).all()
    jsonified_names=jsonify(station_names)
    return(jsonified_names)    
## ---------------------------------------------------------------------------------------------------
@app.route("/api/v1.0/tobs")
def tobs():
    import datetime
    import timestring

    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start_date=timestring.Date(latest_date).date
    lasttwelve=start_date-datetime.timedelta(days=365)
    getdata= session.query(Measurement.date, Measurement.tobs).filter(Measurement.date.between(lasttwelve,start_date))

## creating the dictionary for the display with temperature and dates
    tobs_list={}
    for row in getdata:
       tobs_list[row[0]]=row[1]
    temp_twelvemonths=jsonify(tobs_list)
    return (temp_twelvemonths)
## --------------------------------------------------------------------------------------------------------
# @app.route("/api/v1.0/<start date>")
# def tobs():
#getdata= session.query(Measurement.date, Measurement.tobs).filter(Measurement.date.between(lasttwelve,start_date))
@app.route('/api/v1.0/<start_d>')
def temp_attr_query(start_d):
    return  jsonify(calc_temps(start_d,"2017-08-23"))

@app.route('/api/v1.0/<start_d>/<end_d>')
def temp_attr_querys(start_d, end_d):   
    return   jsonify(calc_temps(start_d,end_d))
##------------------------------------------------------------------------------------------------------------
# @app.route("/api/v1.0/<start>/<end>")
# def start_end(start, end):
#  result=calc_temps('2012-02-28', '2012-03-05')
#  return (jsonify(result))

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    #return("Minimum temperature=", result[0])
# function usage example
#calc_temps('2012-02-28', '2012-03-05')
print(calc_temps('2012-02-28', '2012-03-05'))
##------------------------------------------------------------------------------------------------------------
# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)

### ------------------------------------------------------------------------------------------------------------
