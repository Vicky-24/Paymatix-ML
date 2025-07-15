from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime
import uvicorn, time, os, shutil

from api import customer_churn
from api import bust_out_fraud
from api.config.utils import logger


app = FastAPI()

origin = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# main router
app.include_router(bust_out_fraud.router)
app.include_router(customer_churn.router)

# Custom middleware to measure execution time
async def measure_execution_time_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\n[API Execution Time] '{request.method} {request.url.path} is {execution_time:.3f} seconds'")
    return response

app.middleware('http')(measure_execution_time_middleware)

def clearCache():
    path = os.getcwd()
    # print(path)
    for directories, subfolder, files in os.walk(path):
        if os.path.isdir(directories):
            if directories[::-1][:11][::-1] == '__pycache__':
                shutil.rmtree(directories)

clearCache()

if __name__=='__main__':
    logger.info("-"*70)
    logger.info(f"Program Started @ {datetime.now()}")
    uvicorn.run(app, port=9005)