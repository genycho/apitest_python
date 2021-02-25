#-*- coding: utf-8 -*-
import os, sys, io
import os.path
import requests
import pytest
import json
from datetime import datetime
from common.exceptions import APITestException
from common.api_constants import LogViewerConstants as url_manager

test_email = url_manager.test_email
test_pw = url_manager.test_pw

@pytest.fixture(scope='session')
def get_logfile_idlist(get_lv_baseurl, get_lv_token):
    search_pagesize = 3
    headers = {"Authorization": "Bearer {}".format(get_lv_token(test_email, test_pw))}
    params = {
        'size': search_pagesize
        }
    response = requests.get(lv_api_url + lv_constants.getloglist_api_path, headers=headers, params=params, verify = False)
    if response.status_code != 200:
        raise APITestException("Failed to list search - "+response.status_code)
    response_body = response.json()
    contents_element = response_body.get("content")
    for this_record in contents_element:
        ##### 조회된 모든 데이터에 대해 검색 조건 반영됐는지 for 문 돌면서 확인 
        result_list.append(this_record.get('id'))
    return result_list


def test_logdownload_basic(get_lv_baseurl, get_lv_token, get_logfile_idlist):
    headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(get_lv_token(test_email, test_pw))}
    id_list = get_logfile_idlist(test_email, test_pw)
    payload = {
        "ids": id_list
    }
    response = requests.post(get_lv_baseurl + url_manager.logdownload_api_path, headers=headers, data=json.dumps(payload,indent=4), verify = False)
    assert response.status_code == 200
    response_body = response.json()
    # '"id","transactionId","log","loggedAt","objectKey","host","component","containerId","logLevel","logType","logStatus","updatedAt","createdAt"\n
    # "602efa5c67bd0a718525ca85","","[GW] [DEBUG] 2020-09-15 05:45:54,905 log:228 Internal Server Error: /cxr-v3/predictions/e373d0a5-8aee-4404-9367-f219de0e5d8b/contour.jpg","2020-09-15T05:45:54.905","/tmp/tempLog/host_test_1.container_id_test_1.INFERENCE_SERVER.daily.log.2020-10-16-test.log","host_test_1","INFERENCE_SERVER","container_id_test_1","DEBUG","APP","","2021-02-18T23:38:04.384","2021-02-18T23:38:04.384"\n"602efa5c67bd0a718525ca86","","[BE] [DEBUG] 2020-09-15 05:45:54,905 log:228 Internal Server Error: /cxr-v3/predictions/e373d0a5-8aee-4404-9367-f219de0e5d8b/contour.jpg","2020-09-15T05:45:54.905","/tmp/tempLog/host_test_1.container_id_test_1.INFERENCE_SERVER.daily.log.2020-10-16-test.log","host_test_1","INFERENCE_SERVER","container_id_test_1","DEBUG","APP","","2021-02-18T23:38:04.384","2021-02-18T23:38:04.384"\n"602efa5c67bd0a718525ca87","","[BE] [FATAL] 2020-09-15 05:45:54,905 log:228 Internal Server Error: /cxr-v3/predictions/e373d0a5-8aee-4404-9367-f219de0e5d8b/contour.jpg","2020-09-15T05:45:54.905","/tmp/tempLog/host_test_1.container_id_test_1.INFERENCE_SERVER.daily.log.2020-10-16-test.log","host_test_1","INFERENCE_SERVER","container_id_test_1","FATAL","APP","","2021-02-18T23:38:04.384","2021-02-18T23:38:04.384"\n'
    assert 'id' in response_body
    assert 'transactionId' in response_body
    assert 'log' in response_body
    assert 'loggedAt' in response_body
    assert 'objectKey' in response_body
    assert 'host' in response_body
    assert 'component' in response_body
    assert 'containerId' in response_body
    assert 'logLevel' in response_body
    assert 'logType' in response_body
    assert 'logStatus' in response_body
    assert 'updatedAt' in response_body
    assert 'createdAt' in response_body

