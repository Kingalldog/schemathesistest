import pytest
import logging
import json
from hypothesis import  settings
import schemathesis
from schemathesis import contrib, Case
from schemathesis.contrib.openapi import fill_missing_examples
from schemathesis.checks import response_schema_conformance,negative_data_rejection, not_a_server_error,response_headers_conformance, content_type_conformance
import glamor as allure
from pprint import pformat
from schemathesis import GenerationConfig
from hypothesis import strategies as st

#schemathesis.experimental.STATEFUL_TEST_RUNNER.enable()

def basic_output_schemathesis(case, response):
    allure.attach(attachment_type=allure.attachment_type.JSON, name="Verbose_name",
                  body=pformat(case.endpoint.verbose_name))
    allure.attach(attachment_type=allure.attachment_type.JSON, name="case",
                  body=pformat(case))
    allure.attach(attachment_type=allure.attachment_type.JSON, name="response",
                  body=pformat({"status code:": response.status_code, "body: ": response.text}))

logger = logging.getLogger('MyLogger')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(f"{__name__}.log", mode='a')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)
allure.logging_allure_steps(logger)

with open(f"{__name__}.log", 'w'):
    pass

schema = schemathesis.from_uri("https://petstore.swagger.io/v2/swagger.json")

@schema.parametrize(method="GET", endpoint="/pet/{petId}")
@settings(max_examples=100)
def test_delete_pet_petId(case):
    logger.info(f"\n\n-------{case.endpoint.verbose_name}")
    allure.dynamic.title(f"/{case.endpoint.verbose_name}")
    response = case.call()
    with allure.step(f'Call Test + status: {response.status_code}'):
        with allure.step('Call Method'):
            basic_output_schemathesis(case, response)
        with allure.step('Check Validate'):
            logger.info(f"CASE INFO: {case}")
            case.validate_response(response, checks=(negative_data_rejection,))
