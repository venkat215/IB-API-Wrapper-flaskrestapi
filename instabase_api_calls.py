import requests
import json

def ib_create_folder(env_url, env_token, input_path, folder_name):
    
    URL_BASE = '{}/drives{}/{}/input'.format(env_url, input_path, folder_name)

    api_args=dict(
    type='folder',
    )

    headers = {
        'Authorization': 'Bearer {0}'.format(env_token),
        'Instabase-API-Args': json.dumps(api_args)
    }

    resp = requests.post(URL_BASE, headers=headers, verify = False)

    try:
        resp = resp.json()
        return resp
    except:
        return resp

def ib_create_file(env_url, env_token, input_path, folder_name, file_data, content_type, file_name='input'):

    URL_BASE = '{}/drives{}/{}/input/{}.{}'.format(env_url, input_path, folder_name, file_name, content_type)

    api_args=dict(
    type='file',
    cursor=1,
    if_exists='overwrite'
    )

    headers = {
        'Authorization': 'Bearer {0}'.format(env_token),
        'Instabase-API-Args': json.dumps(api_args)
    }

    resp = requests.post(URL_BASE, headers=headers, data = file_data, verify = False)

    try:
        resp = resp.json()
        return resp
    except:
        return resp

def ib_trigger_flow(env_url, env_token, input_path, folder_name, flow_path):


    URL_BASE = '{}{}'.format(env_url,'/flow/run_flow_async')
    input_dir = '{}/{}/input'.format(input_path, folder_name)

    api_args=dict(
        input_dir= input_dir,
        ibflow_path=flow_path,
        output_has_run_id=False,
        delete_out_dir=True
    )

    headers = {
        'Authorization': 'Bearer {0}'.format(env_token),
        'Instabase-API-Args': json.dumps(api_args)
    }

    data = json.dumps(api_args)

    resp = requests.post(URL_BASE, headers=headers, data = data, verify = False)

    try:
        resp = resp.json()
        return resp
    except:
        return resp
   

def ib_trigger_flows(env_url, env_token, input_path, folder_name, flow_path):
    
    URL_BASE = '{}{}'.format(env_url,'/flow/run_flows_async')
    input_dir = '{}/{}/input'.format(input_path, folder_name)
    
    api_args=dict(
        delete_out_dir=True,
        output_has_run_id=False,
        flow_root_dir=flow_path,
        input_dir=input_dir,
		post_flow_fn='csvs_to_excel'
    )
    headers = {
        'Authorization': 'Bearer {0}'.format(env_token),
        'Instabase-API-Args': json.dumps(api_args)
    }

    data = json.dumps(api_args)

    resp = requests.post(URL_BASE, headers=headers, data=data, verify=False).json()

    try:
        resp = resp.json()
        return resp
    except:
        return resp

def ib_trigger_metaflow(env_url, env_token, input_path, folder_name, flow_path, classifier_path):
    
    URL_BASE = '{}{}'.format(env_url,'/flow/run_metaflow_async')
    input_dir = '{}/{}/input'.format(input_path, folder_name)

    api_args=dict(
        delete_out_dir=True,
        output_has_run_id=False,
        flow_root_dir=flow_path,
        input_dir=input_dir,
        classifier_file_path=classifier_path
    )

    headers = {
        'Authorization': 'Bearer {0}'.format(env_token),
        'Instabase-API-Args': json.dumps(api_args)
    }

    data = json.dumps(api_args)


    resp = requests.post(URL_BASE, headers=headers, data=data, verify=False).json()

    try:
        resp = resp.json()
        return resp
    except:
        return resp

def ib_flow_status(env_url, env_token, job_id):


    URL_BASE = '{}{}{}'.format(env_url,'/jobs/status?job_id=',job_id)

    headers = {
        'Authorization': 'Bearer {0}'.format(env_token),
    }

    resp = requests.get(URL_BASE, headers=headers, data = None, verify = False)

    try:
        resp = resp.json()
        return resp
    except:
        return resp

def ib_flow_output(env, org, country, out_path):

    HOST_URL, API_TOKEN, _, _, _, _ = ib_parameters(env, org, country)

    URL_BASE = '{}{}'.format(HOST_URL.replace('drives',''),'flow/export/review_batch')

    headers = {
        'Authorization': 'Bearer {0}'.format(API_TOKEN),
    }

    out_path = out_path + '/out.ibocr'

    data = {"path": out_path}
    data = json.dumps(data)

    resp = requests.post(URL_BASE, headers=headers, data = data, verify = False)

    try:
        resp = resp.json()
        return resp
    except:
        return resp


def ib_read_file(env_url, env_token, folder_path, file_name):

    URL_BASE = '{}/drives/{}/{}'.format(env_url, folder_path, file_name)

    api_args = dict(
    type='file',
    get_content=True,
    )

    headers = {
    'Authorization': 'Bearer {0}'.format(env_token),
    'Instabase-API-Args': json.dumps(api_args)
    }
    resp = requests.get(URL_BASE, headers=headers, verify = False)

    try:
        # resp = resp.json()
        resp_headers = json.loads(resp.headers['Instabase-API-Resp'])
        data = resp.content

        return (resp_headers, data)

    except:

        try:
            resp = resp.json()
            return resp
        except:
            return resp


def list_dir(env_url, env_token, folder_path, start_page_token, folder_name = None):
    
    URL_BASE = '{}/drives/{}'.format(env_url, folder_path)

    if folder_name:
        URL_BASE = '{}/{}'.format(URL_BASE, folder_name)

    api_args = dict(
    type='folder',
    get_content=True,
    start_page_token=start_page_token
    )

    headers = {
    'Authorization': 'Bearer {0}'.format(env_token),
    'Instabase-API-Args': json.dumps(api_args)
    }

    resp = requests.get(URL_BASE, headers=headers, verify = False)

    try:
        resp = resp.json()
        return resp
    except:
        return resp