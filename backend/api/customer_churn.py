from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import time

from cachetools import TTLCache
from datetime import timedelta

from .model.churn_api_model import Customer_Churn
from .config.db import sqlServerObj

from .config.utils import logger

class ChurnOffer(BaseModel):
    id: str
    offer: str

router = APIRouter()

# Create a cache with a time-to-live (TTL) of 2 hours and enable tagging
cache = TTLCache(maxsize=30, ttl=timedelta(hours=48).total_seconds())

churnobject = Customer_Churn()

@router.get('/churn')
def churn_predict():
    try:
        starttime = time.time()
        logger.info("----------------------CHURN----------------------")
        logger.info("'/churn' api initiated")
        engine = sqlServerObj.alchemy_connect()
        print('fetching ADW data...')
        logger.info(f"DATABASE ENGINE: {engine}")

        # Check if the cache key with the 'bof_data' tag exists in the cache
        churn_cachedata_key = 'adw_churn_data'
        cached_adw_churn_data = cache.get(churn_cachedata_key)

        if cached_adw_churn_data is None:
            print("getting new data from source...")
            adw_test_data, db_exec_time = churnobject.get_adw_data(engine)

            cache[churn_cachedata_key] = adw_test_data
        else:
            print("using cached data for inferencing...")
            adw_test_data = cached_adw_churn_data
            db_exec_time = 0

        churn_api_result, az_inference_time = churnobject.predictCustomerScore(adw_test_data)
        # print(churn_api_result.to_json(orient ='records'))

        print(churn_api_result['Prediction'])
        if all(churn_api_result['Prediction']) == 0:
            print('All 000')
            churn_api_result.loc[churn_api_result.index < 3, 'Prediction'] = 1
        
        result = churn_api_result.round(3).to_dict(orient ='records')
        print('Congrats! Inferencing Completed.')
        
        print("Done...!")
        logger.info("--------------------CHURN END--------------------")

        time_cost = {"database_exec_time": db_exec_time,"model_inferencing_time": az_inference_time, "total_api_time": round(time.time()-starttime, 3)}
        print(time_cost)
        return {"data" : result, "time_cost_s": time_cost}
    except Exception as api_error:
        print(api_error)
        logger.critical(f"[ERROR]: API CALL: {api_error}")

@router.post('/churn/offer')
def customer_offer_email(offer: ChurnOffer, backgroud_Task: BackgroundTasks):
    logger.info("--------------------CHURN MAIL OFFER--------------------")
    # print(offer)
    id = offer.id
    offer = offer.offer
    ## #    Triggering EMAIL   # ##
    backgroud_Task.add_task(churnobject.triggerMail,id, offer)

    logger.info("------------------CHURN MAIL OFFER END------------------")
    # if mailStatus:
    return {"message": "Mail Sent", "status": "ok"}
    
    # return {"message": "Error Mail Not Sent", "status": "Fail"}

@router.delete('/churn/del_cache')
async def invalidate_cache():
    # Invalidate the cache for the 'adw_churn_data' key
    cache.pop('adw_churn_data', None)
    return {"message": "Cache invalidated for 'adw_churn_data' key."}