
#-*- coding: utf-8 -*-
import os,sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import json
import requests
from common import api_test_util as api_util
from common.exceptions import APITestException

###### COMMON ######
# TODO 각 폴더별로 conftest.py를 여러개 만들어 분리
def pytest_addoption(parser):
    parser.addoption("--be_url", action="store", default="http://{my_be_url}", help="Insight Backend test URL. By default: http://{my_be_url}")

def pytest_runtest_setup(item):
  if 'integration' in item.keywords and not item.config.getoption('--integration'):
    pytest.skip('need --integration option to run')


@pytest.fixture(scope='module')
def get_dirpath():
    dirname = os.path.dirname(os.path.abspath(__file__))
    return dirname

@pytest.fixture(scope='session')
def get_be_baseurl(pytestconfig):
    return pytestconfig.getoption("--be_url")

@pytest.fixture(scope='package')
def get_apikey():
    return '{my_api_key}'

@pytest.fixture(scope="session")
def read_testdata_secrets():
    """ 
    테스트에 사용되는 아이디, 비밀번호, API Key 등을 별도 json 파일(dataplatform.json)에 작성 후 최초 테스트 수행 시 읽어오는 fixture. 
    해당 파일은 현재 프로젝트 폴더 경로 상위에 위치하여야 한다 
    """
    parent_dirname = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))  #현재 파일의 4depth 위(프로젝트 바깥) 경로를 얻어오기 
    filename = os.path.join(parent_dirname,'test_data_secret.json')
    try:
        with open(filename, mode='r') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        raise APITestException(f"Failed to get the dataplatform env json file in {filename}")

@pytest.fixture(scope="module")
def get_dicom_uuid(get_be_baseurl, get_apikey, get_dirpath):
    # scope:module 는 module 파일별로 1회 수행 후 재사용된다
    upload_api_path = '/cxr-v3/dcm/'
    headers = {"Authorization": "Bearer "+get_apikey}
    values = {
        "file": ("normal.dcm", open(get_dirpath+"/be/normal.dcm", "rb"))
    }
    response = requests.post(get_be_baseurl + upload_api_path, files=values, headers=headers)
    if 201 != response.status_code:
        raise APITestException("Failed to upload dicom file and get uuid - {}".format(response.text))
    else:
        yield response.json()["uuid"]

@pytest.fixture(scope="module")
def get_case_uuid(get_be_baseurl, get_apikey, get_dicom_uuid):
    predict_api_path = '/cxr-v3/models/latest/predict/'
    dicom_uuid = get_dicom_uuid
    test_threshold_value = 0.25
    headers = {"Content-Type": "application/json", "Authorization": "Bearer "+get_apikey}
    payload = {
        "case": [
            {
                "dicom": dicom_uuid,
                "view_name": "frontal"
            }
        ],
        "threshold": test_threshold_value,
        "filtering": False
    }
    response = requests.post(get_be_baseurl + predict_api_path, data=json.dumps(payload,indent=4), headers=headers)
    if response.status_code != 200:
        raise APITestException("Failed to predict with {}, response{}".format(dicom_uuid,response.text))
    else:
        response_body = response.json()
        if "uuid" in response_body:
            yield response_body.get("uuid")
        else:
            raise APITestException("Failed to predict with {}, response{}".format(dicom_uuid,response.text))




