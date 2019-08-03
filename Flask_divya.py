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
#### This is the home page of the site. It describes the usage with links
#### Displays a picture of hawaiian airplane.
@app.route("/")
def index():
    return '''<strong>Are you going to Hawaii???<br>Check out the weather analysis before you board that flight. Click on the links to explore:</strong> <br> \
    <br>\
    <strong> \
    <a href="http://127.0.0.1:5000/api/v1.0/precipitation" target="_blank">1. /api/v1.0/precipitation</a><br> \
    <br><a href="http://127.0.0.1:5000/api/v1.0/stations" target="_blank">2. /api/v1.0/stations</a><br> \
    <br><a href="http://127.0.0.1:5000/api/v1.0/tobs" target="_blank">3. /api/v1.0/tobs</a><br>\
    <br><a href="http://127.0.0.1:5000/api/v1.0/<start_date>" target="_blank">4. /api/v1.0/YYYY-MM-DD - type the start date in given format in the url<br>\
          to get min, max, avg temperature from your start date less than or equal 2017-08-23</a><br>\
    <br><a href="http://127.0.0.1:5000/api/v1.0/<start_d>/<end_d>" target="_blank">5. /api/v1.0/YYYY-MM-DD/YYYY-MM-DD - type a start date and end date in given format<br>\
        to get  to get min, max, avg temperatures for your time frame. </a><br>
             
    </strong>\
    <br>\
    <img src="https://www.hawaiinewsnow.com/resizer/qRDoOlfikOQD-As0qViLpfliS4w=/1200x600/arc-anglerfish-arc2-prod-raycom.s3.amazonaws.com/public/BHV2ZWBW6BDJVFY3P3EPCDMS34.jpg">
    
    '''

## -------------------------------------------------------------------------------------------
#### Code for precipitation 
@app.route("/api/v1.0/precipitation")
def cal_prcp():
    """Display precipitation for the all the dates from the dataset.
    Args: None
    Returns:
    A jsonified dictionary with all the precipitation readings.
    """
    getdata= session.query(Measurement.prcp, Measurement.date).all()
    summary_dict={}
    for row in getdata:
        summary_dict[row[1]]=row[0]
    return jsonify(summary_dict)
## -------------------------------------------------------------------------------------------------
## Code to list the stations
@app.route("/api/v1.0/stations")
def station_details():
    """Display all the stations from the dataset.
    Args: None
    Returns:
    Jsonified names of all the stations.
    """
    station_names=session.query(Measurement.station).group_by(Measurement.station).all()
    jsonified_names=jsonify(station_names)
    return(jsonified_names)    
## ---------------------------------------------------------------------------------------------------
### Code to display the temperature readings.
@app.route("/api/v1.0/tobs")
def tobs():
    """ Query for the dates and temperature observations from a year from the last data point.
    Args: None
    Returns:
    Return a JSON list of Temperature Observations (tobs) for the previous year.
    """
    import datetime
    import timestring

    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    start_date=timestring.Date(latest_date).date
    lasttwelve=start_date-datetime.timedelta(days=366)
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
@app.route('/api/v1.0/<start_date>')
def temp_attr_query(start_date):
    """ Query for the dates and temperature observations from a year from the last data point.
    Args: None
    Returns:
    Return a JSON list of Temperature Observations (tobs) for the previous year.
    """
    import datetime
    import timestring
    ### Calcualte the last date available in the dataset.
    if start_date > '2017-08-23':
     return("Please enter a start date <= 2017-08-23")
    end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    end_date=timestring.Date(end_date).date
    result=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    ## Add key : values to the result to make it readable.
    summary={'Minumum Temperature':'', 'Maximum Temperature': '', 'Average Temperature': ''}
    for row in result:
        summary['Minumum Temperature']=row[0]
        summary['Maximum Temperature']=row[2]
        summary['Average Temperature']=row[1]
      
    return  (jsonify(summary))

@app.route('/api/v1.0/<start_date>/<end_date>')
def temp_attr_querys(start_date, end_date):  
    """When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` 
       for all dates greater than and equal to the start date.
       When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` 
       for dates between the start and end date inclusive.
       Args: None
       Returns:
       Return a JSON list of the minimum temperature, the average temperature, 
       and the max temperature for a given start or start-end range.
    """
    if end_date > '2017-08-23':
        return("Please enter an end date <= 2017-08-23")

    result=calc_temps(start_date, end_date)
    summary={'Minumum Temperature':'', 'Maximum Temperature': '', 'Average Temperature': ''}
    for row in result:
        summary['Minumum Temperature']=row[0]
        summary['Maximum Temperature']=row[2]
        summary['Average Temperature']=row[1]
      
    return  (jsonify(summary))  
    
##------------------------------------------------------------------------------------------------------------
# Function to calcualte the temperatures.
## -------------------------------------------------------------------------------------------------------
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    if end_date !="":
     return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    else:
        import datetime
        import timestring
    ### Calcualte the last date available in the dataset.
        end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
        end_date=timestring.Date(end_date).date
      
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
print(calc_temps('2012-02-28', '2012-03-05'))
##------------------------------------------------------------------------------------------------------------
# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)

### ------------------------------------------------------------------------------------------------------------
