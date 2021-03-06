#-*- coding: utf-8 -*-
import os,sys
import pytest

import os, sys, io
import requests
import json, time
from common import api_test_util as util
from common.api_constants import LogViewerConstants as url_manager

def test_getcomponent_basic(get_lv_baseurl):
    response = requests.get(get_lv_baseurl + url_manager.getcomponent_api_path, verify=False)
    assert 200 == response.status_code
    response_body = response.json()
    assert len(response_body) == 4
    # '["INSIGHT_BACKEND_MMG","INSIGHT_BACKEND_CXR","INFERENCE_SERVER","GATEWAY"]'
    

def test_getloglevel_basic(get_lv_baseurl):
    response = requests.get(get_lv_baseurl + url_manager.getloglevel_api_path, verify=False)
    assert 200 == response.status_code
    response_body = response.json()
    assert len(response_body) == 5
    # '["DEBUG","WARNING","ERROR","INFO","FATAL"]'

def test_getlogtype_basic(get_lv_baseurl):
    response = requests.get(get_lv_baseurl + url_manager.getlogtype_api_path, verify=False)
    assert 200 == response.status_code
    response_body = response.json()
    assert len(response_body) == 2
    # '["APP","AUDIT"]'















    