from fastapi import APIRouter, BackgroundTasks

from cachetools import TTLCache
from datetime import timedelta

from .model.buf_api_model import BUF_CustomerScore
from .config.db import sqlServerObj
from .config.utils import logger

import time

router = APIRouter()

# Create a cache with a time-to-live (TTL) of 48 hours and enable tagging
cache = TTLCache(maxsize=30, ttl=timedelta(hours=48).total_seconds())
bufobject = BUF_CustomerScore()

@router.get('/')
async def home():
    return """Welcome To Banking Practice Usecases"""

@router.get('/buf')
async def buf_predict(backgroud_Task: BackgroundTasks):
    starttime = time.time()
    logger.info("----------------------BUF----------------------")
    logger.info("'/buf' api called")
    
    engine = sqlServerObj.alchemy_connect()
    logger.info(f"DATABASE ENGINE: {engine}")

    # Check if the cache key with the 'buf_data' tag exists in the cache
    buf_cachedata_key = 'adw_buf_data'
    cached_adw_buf_data = cache.get(buf_cachedata_key)

    if cached_adw_buf_data is None:
        print("getting new data from source...")
        # Cache miss: Fetch data from the database
        adw_test_data, db_exec_time = bufobject.get_adw_data(engine)
        
        # Store the data in the cache with the 'buf_data' key and TTL of 48 hours
        cache[buf_cachedata_key] = adw_test_data
    else:
        print("using cached data for inferencing...")
        adw_test_data = cached_adw_buf_data
        db_exec_time = 0
    
    buf_api_result, az_inference_time = bufobject.predictCustomerScore(adw_test_data)
    grouped_result = buf_api_result.groupby('CustomerID', as_index=False).first()
    # print(json.loads(grouped_result.to_json(orient ='records')))
    
    mod_result = bufobject.modifyDataframe(buf_api_result, grouped_result)
    
    result = mod_result.round(2).to_dict(orient ='records')
    print('Congrats! Inferencing Completed.')
    ##########################
    #    Triggering EMAIL    #
    backgroud_Task.add_task(bufobject.triggerMail,grouped_result)
    print("Done...!")
    logger.info("--------------------BUF END--------------------")

    return {"data" : result, "time_cost_s":{"database_exec_time": db_exec_time,"model_inferencing_time": az_inference_time, "total_api_time": round(time.time()-starttime, 3)}}

@router.delete('/buf/del_cache')
async def invalidate_cache():
    # Invalidate the cache for the 'adw_buf_data' key
    cache.pop('adw_buf_data', None)
    return {"message": "Cache invalidated for 'adw_buf_data' key."}