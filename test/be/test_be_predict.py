#-*- coding: utf-8 -*-
import os, sys, io
import requests
import pytest
import pydicom
import json, time
from common import api_test_util as util
from common.exceptions import APITestException

this_api_path = '/cxr-v3/models/latest/predict/'

def test_predict_200ok(get_be_baseurl, get_apikey, get_dicom_uuid):
    test_uuid = get_dicom_uuid
    test_threshold_value = 0.25
    headers = {"Content-Type": "application/json", "Authorization": "Bearer "+get_apikey}
    payload = {
        "case": [
            {
                "dicom": test_uuid,
                "view_name": "frontal"
            }
        ],
        "threshold": test_threshold_value,
        "filtering": False
    }
    response = requests.post(get_be_baseurl + this_api_path, data=json.dumps(payload,indent=4), headers=headers)

    assert 200 == response.status_code, "Failed to predict!! - "+response.text

    response_body = response.json()
    # assert test_uuid == response_body.get("uuid") ?? 다른 uuid가 반환됨
    assert "uuid" in response_body
    assert "inference_model" in response_body
    child_inference_model = response_body.get("inference_model")
    assert "tag" in child_inference_model
    assert "description" in child_inference_model
    assert "supported_features" in child_inference_model
    assert "case" in response_body
    first_case = response_body.get("case")[0]
    assert "dicom" in first_case
    assert "view_name" in first_case
    # deleted!!
   


def test_predict_dupuuid(get_be_baseurl, get_apikey, get_dicom_uuid):
    """ 동일 uuid에 대해 2번 분석 시도 """
    test_uuid = get_dicom_uuid
    headers = {"Content-Type": "application/json", "Authorization": "Bearer "+get_apikey}
    payload = {
        "case": [
            {
                "dicom": test_uuid,
                "view_name": "frontal"
            }
        ],
        "threshold": 0.15,
        "filtering": False
    }

    # 최초 분석시도
    response = requests.post(get_be_baseurl + this_api_path, data=json.dumps(payload,indent=4), headers=headers)

    assert 200 == response.status_code, "첫번째 분석에 실패하였습니다"
    response_body = response.json()
    assert "uuid" in response_body
    print(f"first result uuid = {response_body.get('uuid')}")

    # 다시 분석시도
    response = requests.post(get_be_baseurl + this_api_path, data=json.dumps(payload,indent=4), headers=headers)

    assert 200 == response.status_code, "두번째 분석에 실패하였습니다"+response.text
    response_body = response.json()
    assert "uuid" in response_body
    print(f"second result uuid = {response_body.get('uuid')}")
    assert "inference_model" in response_body
    # deleted!!


def test_predict_bodynocase(get_be_baseurl, get_apikey):
    headers = {"Content-Type": "application/json", "Authorization": "Bearer "+get_apikey}
    payload = {
        # "case": [
        #     {
        #         "dicom": test_uuid,
        #         "view_name": "frontal"
        #     }
        # ],
        "threshold": 0.15,
        "filtering": False
    }
    response = requests.post(get_be_baseurl + this_api_path, data=json.dumps(payload,indent=4), headers=headers)

    assert 400 == response.status_code
    # '{"message":"case: This field is required.","code":400,"insight_error_code":"400.50.ISTBE.004"}'
    response_body = response.json()
    assert "code" in response_body
    assert "insight_error_code" in response_body
    assert "case: This field is required." == response_body.get("message")
    assert "400.50.ISTBE.004" == response_body.get("insight_error_code")

def test_predict_bodynoparameters(get_be_baseurl, get_apikey, get_dicom_uuid):
    """ when no threshold, filtering, checking default value and beviour """
    test_uuid = get_dicom_uuid
    headers = {"Content-Type": "application/json", "Authorization": "Bearer "+get_apikey}
    payload = {
        "case": [
            {
                "dicom": test_uuid,
                "view_name": "frontal"
            }
        ]
        # "threshold": 0.15,
        # "filtering": False
    }
    response = requests.post(get_be_baseurl + this_api_path, data=json.dumps(payload,indent=4), headers=headers)

    assert 200 == response.status_code
    response_body = response.json()
    assert "uuid" in response_body
    assert "inference_model" in response_body
    child_inference_model = response_body.get("inference_model")
    assert "tag" in child_inference_model
    assert "description" in child_inference_model
    assert "supported_features" in child_inference_model
    assert "case" in response_body
    first_case = response_body.get("case")[0]
    assert "dicom" in first_case
    print(f"dicom id = {first_case.get('dicom')}")
    assert "view_name" in first_case
    #### 디폴트 값 처리 확인 ####
    assert 0.15 == response_body.get("threshold"), "기대한 threshold 디폴트값과 다릅니다!"
    assert False == response_body.get("filtering")
    ############################
    
    assert "status" in response_body

@pytest.mark.skip(reason="filtering 설정하는 방법 파악 후 설정")
def test_predict_filteringon(get_be_baseurl, get_apikey, get_dicom_uuid):
    """ 필터링 True했을 때 동작 확인. ToDo 필터링하는 값을 따로 줘야할것 같은데?  """
    test_uuid = get_dicom_uuid
    headers = {"Content-Type": "application/json", "Authorization": "Bearer "+get_apikey}
    payload = {
        "case": [
            {
                "dicom": test_uuid,
                "view_name": "frontal"
            }
        ],
        "threshold": 0.15,
        "filtering": True
    }
    response = requests.post(get_be_baseurl + this_api_path, data=json.dumps(payload,indent=4), headers=headers)
    assert 200 == response.status_code


def test_predict_invalidapikey(get_be_baseurl, get_apikey, get_dicom_uuid):
    test_uuid = get_dicom_uuid
    headers = {"Content-Type": "application/json", "Authorization": "Bearer "+ "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiYWI4NzVkYS03ZWUxLTRmYzYtOTNiOC1mZWIxZDIwY2E5NzUiLCJpc3MiOiJMdW5pdCIsImlhdCI6MTYwNjExMjc4MCwiZXhwIjoxNjEzODg4NzgwLCJuYmYiOjE2MDYxMTI3ODAsImF1ZCI6Imh0dHBzOi8vaW5zaWdodC5sdW5pdC5pbyIsImRhdGEiOnsiY291bnRyeV9pZCI6MSwiY291bnRyeV9uYW1lIjoiQWZnaGFuaXN0YW4ifX0.XEmOg5ZBZiHyzhcZJRuu12J-_VxyGfbvVPWygee23qc"}
    payload = {
        "case": [
            {
                "dicom": test_uuid,
                "view_name": "frontal"
            }
        ],
        "threshold": 0.15,
        "filtering": False
    }

    response = requests.post(get_be_baseurl + this_api_path, data=json.dumps(payload,indent=4), headers=headers)
    assert 401 == response.status_code


