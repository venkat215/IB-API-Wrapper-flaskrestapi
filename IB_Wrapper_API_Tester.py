import requests
import json
import logging
import time
import base64

def trigger_flow():
    
    # logging.info('pinging home URL for response')
    print('pinging home URL for response')

    url = "http://10.23.218.102:5000"
    # url = "http://127.0.0.1:5000"
    resp_data = requests.get(url, verify = False)
    resp_json = resp_data.json()
    print(resp_json)

    # logging.info('Fetching JWT')
    print('Fetching JWT without app_name')

    client_id = ''
    client_secret = ''

    encoded_token = base64.b64encode(client_id + ":" + client_secret)

    headers = {"Authorization" : "Basic {}".format(encoded_token)}
    url = "http://10.23.218.102:5000/token"
    # url = "http://127.0.0.1:5000/token"

    resp_data = requests.get(url, headers = headers, verify = False)
    resp_json = resp_data.json()
    print(resp_json)

    try:

        app_name = resp_json['Available Applications'][0]

        print('Fetching JWT with app_name')

        client_id = ''
        client_secret = ''

        encoded_token = base64.b64encode(client_id + ":" + client_secret)

        headers = {"Authorization" : "Basic {}".format(encoded_token), "app_name" : app_name}
        url = "http://10.23.218.102:5000/token"
        # url = "http://127.0.0.1:5000/token"

        resp_data = requests.get(url, headers = headers, verify = False)
        resp_json = resp_data.json()
        print(resp_json)

    except:

        pass
        
    jwt = resp_json['jwt']

    # logging.info('Trigger Datalocker Flow')
    print('Trigger Datalocker Flow')

    headers = {"jwt" : jwt, "mime-type" : "json"} #, "file-name" : "input"
    data = '{"records":[{"query_name":"filenet_args","json_params":{"doctype":["PAN","PST"],"input_stream":"","consumerInputParams":{"srcRefNo":708694424,"country":"IN","taskId":708694424},"domain":"HK","docClsName":"RTLDoc","doc_type":"","osName":"RBOS","docIds":["{11BA62F0-E03D-4B20-BEE6-67C412B8591E}","{68180EF8-14A5-4AA4-B413-0A7CD50C8FC3}"],"MimeType":""}}]}'
    url = "http://10.23.218.102:5000/trigger_flow"
    # url = "http://127.0.0.1:5000/trigger_flow"

    resp_data = requests.post(url, headers = headers, data = data, verify = False)
    resp_json = resp_data.json()

    print(resp_json)

    # logging.info('Getting Flow Output')
    print('Getting Flow Output')

    job_id = resp_json['job_id'] #'b5b2e62b-3444-498f-b05b-9d7122de5684'
    ib_output_folder = resp_json['ib_output_folder'] #'DataLocker/Datalocker_Single_Flow/fs/Instabase Drive/samples/consumer_input/1561498676/out'
    state = "PENDING"
    n=0

    while state == "PENDING":
        
        time.sleep(10)

        headers = {"jwt" : jwt}
        data = json.dumps({"job-id" : job_id, "ib-output-folder" : ib_output_folder, "job-id" : job_id, "ib-output-folder" : ib_output_folder})
        url = "http://10.23.218.102:5000/flow_status"
        # url = "http://127.0.0.1:5000/flow_status"

        resp_data = requests.get(url, headers = headers, data = data, verify = False)

        flow_state_json = resp_data.json()
        
        if not n:
            # logging.info('Logging Pending repsonse only one time for reference. Loop continues until flow completes.')
            print('Logging Pending repsonse only one time for reference. Loop continues until flow completes.')
            print(flow_state_json)
            n+=1

        try:
            state = flow_state_json['ib_response']['state']
        except:
            state = "DONE"

    # logging.info('Printing Flow Output')
    print('Printing Flow Output')
    print(resp_data.content)

def manual_read():

    jwt = {u'jwt': u''}['jwt']
    # logging.info('Reading file manually')
    print('Reading file manually')

    headers = {"jwt" : jwt}
    data = json.dumps({"folder-path" : "DataLocker/Datalocker_Single_Flow/fs/Instabase Drive/samples/consumer_input/CKUXKRUOZK20190702155721213137/out", "file-name" : "IB_OP.json"})
    url = "http://10.23.218.102:5000/read_file"
    # url = "http://127.0.0.1:5000/read_file"

    resp_data = requests.get(url, headers = headers, data = data, verify = False)

    print(resp_data.content)

trigger_flow()
# manual_read()