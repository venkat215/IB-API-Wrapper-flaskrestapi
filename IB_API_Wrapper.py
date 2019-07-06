from gevent import monkey
monkey.patch_all()
from flask import Flask, request, Response
import cx_Oracle
from ibwrapper_endpoint_methods import End_Point_Methods
import logging
import json
import sys
import datetime

#load config file
try:
    config = json.load(open('resources/config/config.json', 'r'))
    # config = json.load(open('resources\\config\\config.json', 'r'))

#Initialize Flask App
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config['app_secret_key']

#Set logger to gunicorn logger
    if __name__ != '__main__':
    	gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

#Create the Database Connection Pool
    user = config['db_user']
    password = config['db_password']
    db = config['db']
    db_pool = cx_Oracle.SessionPool(user, password, db, 2, 10, 3)

    #Import the End point functions
    end_point_methods = End_Point_Methods(db_pool, app.logger)

except Exception as e:

    app.logger.error(str(e))
    sys.exit(1)

#Home method for testing if server is running
@app.route('/', methods=['GET'])
def home():
    
    try:
        return Response(json.dumps({"Response" : "Success"}), status=200)
    except Exception as e:
        time_of_error = datetime.datetime.now()
        logging.error(str(e) + ". Time_of_error : "+ str(time_of_error))
        return Response(json.dumps({"error_msg":"Error_processing_your_request. Contact support team",
                                 "time_of_error" : str(time_of_error)}), status=501)

#Generates JWT for the user.
@app.route('/token', methods=['GET'])
def generate_jwt():

# User need to provide the folowing headers:
#Authorization : provided at the time of registration with the service
# "app_name" : "Name of app from one of the available apps"
#sample_curl_command:
# curl -k -X GET -H 'Authorization: Basic cmV0YWlsOlIzN2ExTCMxMjM=' -H "app_name" : "DataLocker" http://<base_url>/get_token

    try:

        headers = request.headers
        jwt_response, status_code = end_point_methods.generate_jwt(headers)
        return Response(json.dumps(jwt_response), 200)
        

    except Exception as e:

        time_of_error = str(datetime.datetime.now())
        app.logger.error(str(e) + ". Time_of_error : " + time_of_error + ". Endpoint : get_token")
        return Response(json.dumps({"error_msg":"Error_processing_your_request. Contact support team",
                                 "time_of_error" : str(time_of_error)}), status=501)

#Uploads input content and triggers the respective flow based on the user
@app.route('/trigger_flow', methods=['POST'])
def trigger_flow():
    
# Requires input file as data and the following headers
#jwt : provided by IB_Wrapper
#content-type: eg.json, txt, pdf, xls etc.
#file-name: if_not provided will be defaulted to input. 
# pass filestream or file_content in data

#sample_curl_command:
#curl -X POST -H 'http://<base_url>/trigger_flow' # -H 'jwt:<jwt_token>' -H 'content_type:json'  -d <data>

    try:
        
        headers = request.headers
        data = request.data
        response, status_code = end_point_methods.trigger_flow(headers, data)
        return Response(json.dumps(response), status_code)

    except Exception as e:
        
        time_of_error = datetime.datetime.now()
        app.logger.error(str(e) + ". Time_of_error : "+ str(time_of_error))
        return Response(json.dumps({"error_msg":"Error_processing_your_request. Contact support team",
                                 "time_of_error" : str(time_of_error)}), status=501)

#Uploads input content and triggers the respective flow based on the user
@app.route('/flow_status', methods=['GET'])
def flow_Status():

# Requires following headers
#jwt : provided by IB_Wrapper
#job-id: received when flow was triggered
#ib-output-folder: received when flow was trigerred

#sample_curl_command:
#curl -X POST -H 'http://<base_url>/flow_status' # -H 'jwt:<jwt_token>' -H 'job_id:<job_id>'  -H ib_output_folder:<ib_output_folder>

    try:

        headers = request.headers
        data = request.data
        response, status_code = end_point_methods.get_flow_status(headers, data)
        return Response(json.dumps(response), status_code)

    except Exception as e:
        
        time_of_error = datetime.datetime.now()
        app.logger.error(str(e) + ". Time_of_error : "+ str(time_of_error))
        return Response(json.dumps({"error_msg":"Error_processing_your_request. Contact support team",
                                 "time_of_error" : str( time_of_error)}), status=501)


#Uploads input content and triggers the respective flow based on the user
@app.route('/read_file', methods=['GET'])
def read_file():

# Requires following headers
#jwt : provided by IB_Wrapper
#folder-path: recieved while enquiring flow status
#file-name: One of the files received recieved  in an array while enquiring flow status

#sample_curl_command:
#curl -X POST -H 'http://<base_url>/flow_status' # -H 'jwt:<jwt_token>' -H 'folder_path:<folder_path>'  -H file_name:<file_name>

    try:
        
        headers = request.headers
        data = request.data
        response, status_code = end_point_methods.read_file(headers, data)
        return Response(json.dumps(response), status_code)

    except Exception as e:
        
        time_of_error = datetime.datetime.now()
        app.logger.error(str(e) + ". Time_of_error : "+ str(time_of_error))
        return Response(json.dumps({"error_msg":"Error_processing_your_request. Contact support team",
                                 "time_of_error" : str(time_of_error)}), status=501)

#Run Server
def run_server():
    
    app.debug = False
    app.run()

#Start the server
if __name__ == '__main__':

    run_server()

