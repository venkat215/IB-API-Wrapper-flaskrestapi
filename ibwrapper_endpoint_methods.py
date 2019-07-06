import json
import base64
import uuid
import instabase_api_calls
import jwt
import datetime
import random
import string
import re

def randomString(stringLength=5):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    str__ = ''.join(random.choice(letters) for i in range(stringLength)).upper()
    time__ = ''.join(re.findall(r'[0-9]', str(datetime.datetime.now())))
    return str__ + time__

class End_Point_Methods():

    def __init__(self, db_pool, logger):
        
        self.db_pool = db_pool
        self.logger = logger
        self.queries = json.load(open('resources/queries/queries.json', 'r'))
        # self.queries = json.load(open('resources\\queries\\queries.json', 'r'))
        with open('resources/certs/filenethkappsf51.hk.standardchartered.com.pem', 'r') as f:
        # with open('resources\\certs\\filenethkappsf51.hk.standardchartered.com.pem', 'r') as f:
            self.priv_cert = f.read()
            f.close()
        with open('resources/certs/filenethkappsf51.hk.standardchartered.com.cer', 'r') as f:
        # with open('resources\\certs\\filenethkappsf51.hk.standardchartered.com.cer', 'r') as f:
            self.pub_cert = f.read()
            f.close()
        self.constants = json.load(open('resources/constants/constants.json', 'r'))
        # self.constants = json.load(open('resources\\constants\\constants.json', 'r'))

    #Excute DB Queries
    def db_connect(self, query_to_execute):

        conn = self.db_pool.acquire()
        cur = conn.cursor()
        cur.execute(query_to_execute)
        return cur

    # def register_user(self, client_name, client_password):
        
        # client_id = uuid.uuid1()
        # print(str(client_id))

        # client_secret = base64.b64encode(client_password)

        # print(client_secret)
        # # client_secret = uuid.uuid3(client_id, client_password_endcoded)
        # # client_secret_encoded = base64.b64encode(client_name + client_secret.hex)
        # # print(client_secret_encoded)

        # access_token = base64.b64encode(str(client_id) + ':' + client_secret)
        # print(access_token)

        # now = datetime.datetime.now().date()
        # plus_one_year = now + datetime.timedelta(days=365)

        # print(base64.b64encode(str(plus_one_year)))

    def generate_jwt(self, headers):
        
        try:
            base_encoded_token = str(headers['Authorization']).split(' ')[1]
        except:
            return {"error_msg" :"Invalid Token"}, 400
        
        decoded = base64.b64decode(base_encoded_token)

        client_id , client_secret = decoded.split(':',1)

        sql_query = self.queries['combined_query']

        try:
            app_name = headers['app_name']
            app_name_str_ = "AND APP.APP_NAME = '{}'".format(app_name)
        except:
            app_name_str_ = ''

        try:
            country = headers['country']
            country_str_ = "AND APP.COUNTRY = '{}'".format(country)
        except:
            country_str_ = ''

        sql_query = sql_query.format(client_id, client_secret, app_name_str_, country_str_)

        try:
            cur = self.db_connect(sql_query)
        except Exception as e:

            time_of_error = datetime.datetime.now()
            self.logger.error(str(e) + ". Time_of_error : " + str(time_of_error) + ". Method : db_connect")

            return {"error_msg" :"Failed to contact DB", "error_msg" : str(e)}, 501
        
        line = None
        query_results = []

        headers = [i[0] for i in cur.description]

        for line in cur:
            query_results.append([line[headers.index('APP_NAME')], line[headers.index('COUNTRY')]])

        if not line:
            return {"error_msg" :"Invalid Token andd / or app_name / country_name"}, 400
        
        if len(query_results) > 1:
            return {"error_msg" :"Dear Client. You have access to multiple applications. Please specify the required application in your headers as part of the request",
                    "header_format" : '"app_name" : "Select one from available applications", "country" : "Select one from available countries"',
                    "available_applications" : query_results}, 400

        now = datetime.datetime.now()
        now_plus_expiry = now + datetime.timedelta(minutes = self.constants['jwt_expire_mins'])
        now_plus_expiry_str = now_plus_expiry.strftime("%d-%b-%Y (%H:%M:%S.%f)")
                
        if datetime.datetime.now().date() > datetime.datetime.strptime(base64.b64decode(line[headers.index('TIMEOUT')]),'%Y-%m-%d').date():
            return {"Time_Out_Error" :"Your access to the requested flow has expired. Please request for access again"}, 400
        
        payload = {"data" : base64.b64encode(str({"time_out" : line[headers.index('TIMEOUT')],
                                                  "app_name" : line[headers.index('APP_NAME')],
                                                  "country" : line[headers.index('COUNTRY')],
                                                  "input_path" : line[headers.index('INPUT_FLDR_PATH')],
                                                  "workflow_path" : line[headers.index('FLOW_PATH')],
                                                  "classifier_path" : line[headers.index('CLASSIFIER_PATH')],
                                                  "output_file" : line[headers.index('OUTPUT_FILE_FOLDER')],
                                                  "mime_type" : line[headers.index('MIME_TYPE')],
                                                  "env_url" : line[headers.index('ACT_URL')],
                                                  "env_token" : line[headers.index('ACT_ACS_TKN')],
                                                  "exp" : now_plus_expiry,
                                                  "iss" : self.constants['issuer'],
                                                  "iat" : now,
                                                  "expiry" : now_plus_expiry_str})),
                   "urls" : {"trigger_flow" : "http://10.23.218.102:5000/trigger_flow",
                             "get_job_status" : "http://10.23.218.102:5000/get_job_status",
                             "get_file" : "http://10.23.218.102:5000/get_file"}}
        
        encoded_jwt = jwt.encode(payload, self.priv_cert, algorithm='RS256')
        return {"jwt" : encoded_jwt}, 200

    def decode_jwt(self, encoded_jwt):
        
        jwt_payload = eval(base64.b64decode(jwt.decode(encoded_jwt,  self.pub_cert, algorithms=['RS256'], verify=False)['data']))
        current_time = datetime.datetime.now()
        expiry_time = datetime.datetime.strptime(jwt_payload['expiry'], "%d-%b-%Y (%H:%M:%S.%f)")
        if current_time > expiry_time:
            return ({"status" : "Error", "error_msg" :"JWT Expired"}, 400)
        if datetime.datetime.now().date() > datetime.datetime.strptime(base64.b64decode(jwt_payload['time_out']),'%Y-%m-%d').date():
            return ({"status" : "Error", "error_msg" :"Your access to the requested flow has expired. Please request for access again"}, 400)

        return jwt_payload

    def trigger_flow(self, headers, data):

        try:
            jwt_payload  = self.decode_jwt(headers['jwt'])
            if type(jwt_payload) == tuple:
                return jwt_payload[0], jwt_payload[1]
        except Exception as e:
            time_of_error = datetime.datetime.now()
            self.logger.error(str(e) + ". Time_of_error : " + str(time_of_error) + ". Method : decode_jwt")
            return {"status" : "Error", "error_msg" : {"jwt_validation_error" :  str(e)}}, 501
        
        try:
            content_type = headers['mime-type']
            try:
                file_name = headers['file-name']
            except:
                file_name = 'input'

        except KeyError as e:
            time_of_error = datetime.datetime.now()
            self.logger.error(str(e) + ". Time_of_error : " + str(time_of_error) + ". Header Error : Valid header not provided")
            return {"status" : "Error", "error_msg" : "One of the required headers in missing", "Missing header" : str(e)}, 400
        
        if not data:
            return {"status" : "Error", "error_msg" : "File data not provided"}, 400

        input_path = jwt_payload['input_path']
        workflow_path = jwt_payload['workflow_path']
        classifier_path = jwt_payload['classifier_path']
        env_url = jwt_payload['env_url']
        env_token = jwt_payload['env_token']
        task_id = randomString()
           
        # create_input_directory
        resp = instabase_api_calls.ib_create_folder(env_url = env_url, env_token = env_token, input_path = input_path, folder_name = str(task_id))
        
        try:
            if resp[u'status'] != 'OK':
                return {"status" : "Error", "error_msg" : "Input Folder Creation Error, Folder Not Created. Try Again", "ib_response" : resp}, 501
        except:
                return {"status" : "Error", "error_msg" : "Input Folder Creation Error, Folder Not Created. Try Again", "ib_response" : resp}, 501     

        # upload_files
        resp = instabase_api_calls.ib_create_file(env_url = env_url, env_token = env_token, input_path = input_path, folder_name = str(task_id), file_name = file_name, file_data = data, content_type = content_type)
        
        try:
            if resp[u'status'] != 'OK':
                return {"status" : "Error", "error_msg" : "Input File Creation Error, File Not Created. Try Again", "ib_response" : resp}, 501
        except:
                return {"status" : "Error", "error_msg" : "Input File Creation Error, File Not Created. Try Again", "ib_response" : resp}, 501     

        #trigger_flow
        if classifier_path:
            resp = instabase_api_calls.ib_trigger_metaflow(env_url = env_url, env_token = env_token, input_path = input_path, folder_name = str(task_id), flow_path = workflow_path, classifier_path = classifier_path)
        elif workflow_path.find('.ibflow') != -1:
            resp = instabase_api_calls.ib_trigger_flow(env_url = env_url, env_token = env_token, input_path = input_path, folder_name = str(task_id), flow_path = workflow_path)
        else:
            resp = instabase_api_calls.ib_trigger_flows(env_url = env_url, env_token = env_token, input_path = input_path, folder_name = str(task_id), flow_path = workflow_path)
        
        #send response 
        try:
            job_id = resp[u'data'][u'job_id']
            output_path = resp[u'data'][u'output_folder']
            
            return {"status" : "Running",
                    "job_id" : job_id,
                    "ib_output_folder" : output_path}, 200  
        except:

            return {"status" : "Error", "error_msg" : "Flow not triggered. Try Again", "error_msg" : resp}, 501   

    def get_flow_status(self, headers, data):
        
        try:
            jwt_payload  = self.decode_jwt(headers['jwt'])
            if type(jwt_payload) == tuple:
                return jwt_payload[0], jwt_payload[1]
        except Exception as e:
            time_of_error = datetime.datetime.now()
            self.logger.error(str(e) + ". Time_of_error : " + str(time_of_error) + ". Method : decode_jwt")
            return {"status" : "Error", "error_msg" : {"jwt_validation_error" :  str(e)}}, 501
        
        try:
            data_dict = json.loads(data)
        except:
            time_of_error = datetime.datetime.now()
            self.logger.error(str(e) + ". Time_of_error : " + str(time_of_error) + ". Data type Error : Data format not json")
            return {"status" : "Error", "error_msg" : "Data format not json"}, 400
        
        try:
            job_id = data_dict['job-id']
            ib_output_folder = data_dict['ib-output-folder']

        except KeyError as e:
            time_of_error = datetime.datetime.now()
            self.logger.error(str(e) + ". Time_of_error : " + str(time_of_error) + ". Header Error : Valid header not provided")
            return {"status" : "Error", "error_msg" : "One of the required headers in missing", "Missing header" : str(e)}, 400
    
        output_file_name = jwt_payload['output_file']
        mime_type = jwt_payload['mime_type']
        env_url = jwt_payload['env_url']
        env_token = jwt_payload['env_token']

        resp = instabase_api_calls.ib_flow_status(env_url = env_url, env_token = env_token, job_id = job_id)

        #send response 
        try:
            if resp[u'state'] == "PENDING":
                return {"status" : "Running",
                        "ib_response" : resp,
                        "job_id" : job_id,
                        "ib_output_folder" : ib_output_folder}, 200

            if resp[u'status'] == "ERROR":
                return {"status" : "Error",
                        "ib_response" : resp,
                        "job_id" : job_id,
                        "ib_output_folder" : output_path}, 200
            
            current_status = resp[u'cur_status']

            if mime_type != "ls":
                
                headers_internal = {'env_url' : env_url, 'env_token' : env_token, 'folder_path' : ib_output_folder, 'file_name' : output_file_name}
                return self.read_file(headers_internal, internal = True)

            else:

                    has_more = True
                    next_page_token = None

                    page_wise = {}
                    n = 1

                    try:

                        while has_more:

                            resp = instabase_api_calls.list_dir(env_url = env_url, env_token = env_token, start_page_token = next_page_token, folder_path = ib_output_folder)
                            page_wise['Page_' + str(n)] = resp[u'nodes']
                            has_more = resp[u'has_more']
                            next_page_token = resp['next_page_token']
                            n+= 1

                        return {"status" : "Done", "Pagewise List of Files" : page_wise}, 200
                    
                    except:
                            
                            has_more = False
                            return {"error_msg" : "Unable to list output directory. Try Again", "ib_response" : resp}, 501  

        except:
            return {"error_msg" : "Error fetching output files. Try Again", "ib_response" : resp}, 501   

    def read_file(self, headers, data = None, internal = False):

        if not internal:
            try:
                jwt_payload  = self.decode_jwt(headers['jwt'])
                if type(jwt_payload) == tuple:
                    return jwt_payload[0], jwt_payload[1]
            except Exception as e:
                time_of_error = datetime.datetime.now()
                self.logger.error(str(e) + ". Time_of_error : " + str(time_of_error) + ". Method : decode_jwt")
                return {"status" : "Error", "error_msg" : {"jwt_validation_error" :  str(e)}}, 501
            
            try:
                data_dict = json.loads(data)
            except:
                time_of_error = datetime.datetime.now()
                self.logger.error(str(e) + ". Time_of_error : " + str(time_of_error) + ". Data type Error : Data format not json")
                return {"status" : "Error", "error_msg" : "Data format not json"}, 400
            
            try:
                folder_path = data_dict['folder-path']
                file_name = data_dict['file-name']

            except KeyError as e:
                time_of_error = datetime.datetime.now()
                self.logger.error(str(e) + ". Time_of_error : " + str(time_of_error) + ". Header Error : Valid header not provided")
                return {"status" : "Error", "error_msg" : "One of the required headers in missing", "Missing header" : str(e)}, 400

            env_url = jwt_payload['env_url']
            env_token = jwt_payload['env_token']
        
        else:
            
            env_url = headers['env_url']
            env_token = headers['env_token']   
            folder_path = headers['folder_path']
            file_name = headers['file_name']
        
        resp = instabase_api_calls.ib_read_file(env_url = env_url, env_token = env_token, folder_path = folder_path, file_name = file_name)
        
        try:
            if type(resp) != tuple:
                return {"status" : "Error", "error_msg" : "Error fetching output files. Try Again", "ib_response" : resp}, 501

            resp_headers = resp[0]
            data = resp[1]

            if resp_headers['status'] == "ERROR" or not data:
                return {"status" : "Error", "error_msg" : "Output File Missing. Requested file/folder not available in path. Please verify the file path provided", "ib_response" : resp_headers}, 400

            return {"status" : "Success",
                    "output_file_name" : file_name,
                    "output_file_data" : data}, 200

        except:
            return {"status" : "Success", "Output File Error" : "Error fetching output files. Try Again", "error_msg" : resp}, 501