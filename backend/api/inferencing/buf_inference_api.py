import urllib.request
import json
import os
import ssl
import pandas as pd

from ..config.config_details import BUF_MODEL_ENDPOINT, BUF_DEPLOYMENT_NAME, BUF_MODEL_API_KEY
from ..config.utils import logger, measure_execution_time

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script

url = BUF_MODEL_ENDPOINT
# Replace this with the primary/secondary key or AMLToken for the endpoint
api_key = BUF_MODEL_API_KEY
deployment_name = BUF_DEPLOYMENT_NAME
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")

# The azureml-model-deployment header will force the request to go to a specific deployment.
# Remove this header to have the request observe the endpoint traffic rules
headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': deployment_name }

@measure_execution_time
def azure_buf_predict(data):
  print('waiting for results from AzureML Model...')
  # logger.info(f"API BODY FOR INFERENCING:\n{data}")
  logger.info('waiting for results from AzureML Model...')
  body = str.encode(json.dumps(data))
  req = urllib.request.Request(url, body, headers)
  try:
    response = urllib.request.urlopen(req)
    result = response.read()
    # logger.info(f"RAW API RESPONSE FROM INFERENCING ENDPOINT:\n{result}") ## Very Long Response
    
    result = json.loads(result)
    api_result = pd.DataFrame(result)
    # print(api_result)
    # logger.info(f"PROCESSED API RESULT:\n{api_result}") ## Very Long Response
    logger.info(f"Inferencing Completed!")

    return api_result
  except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))
    logger.critical(f"[ERROR] INFERENCE ENDPOINT ERROR: {str(error)}")
    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))