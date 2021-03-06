#-*- coding: utf-8 -*-
import os,sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
import json
import requests
from common import api_test_util as api_util
from common.exceptions import APITestException
from common.api_constants import LogViewerConstants as lv_constants

@pytest.fixture(scope='session')
def get_lv_token(get_lv_baseurl):
    def _data(test_email, test_pw):
        headers = {"Content-Type": "application/json"}
        payload = {
            "email": test_email,
            "password": test_pw
        }
        response = requests.post(get_lv_baseurl + lv_constants.login_api_path, data=json.dumps(payload,indent=4), headers=headers, verify=False)
        if response.status_code == 200: 
            response_body = response.json()
            return response_body.get("accessToken")
        else:
            raise APITestException("Failed to login - status_code: {}, {}".format(response.status_code, response.text))    
    return _data


