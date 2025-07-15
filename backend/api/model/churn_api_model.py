import pandas as pd
import json

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl

from ..inferencing.churn_inference_api import azure_churn_predict
from ..config.config_details import *
from ..config.utils import logger, measure_execution_time

class Customer_Churn:

    @measure_execution_time
    def get_adw_data(self, engine):
        logger.info(f"FETCHING DATA FROM ADW {CHURN_TABLE_NAME}")

        dataset = pd.read_sql_table(CHURN_TABLE_NAME, engine)
        # dataset = pd.read_sql_query(f"SELECT * FROM {CHURN_TABLE_NAME};", engine)

        dataset_all = dataset
        dataset_all.drop(columns=["churn", "action", "explanation"], inplace=True, errors='ignore')
        dataset_all.fillna(0, inplace=True)
        dataset_all.rename(columns = {
                    "avgotb": "Avg_Open_To_Buy",
                    "avgutilratio": "Avg_Utilization_Ratio",
                    "cardcategory": "Card_Category",
                    "creditlimit": "Credit_Limit",
                    "cust_age": "Customer_Age",
                    "cust_id": "Customer_ID",
                    "dependentcount": "Dependent_count",
                    "edulevel": "Education_Level",
                    "gender": "Gender",
                    "inactivemonths": "Months_Inactive_12_mon",
                    "incomecategory": "Income_Category",
                    "maritalstatus": "Marital_Status",
                    "mob": "Months_on_book",
                    "totalamtchange": "Total_Amt_Chng_Q4_Q1",
                    "totalctchange": "Total_Ct_Chng_Q4_Q1",
                    "totalrelcount": "Total_Relationship_Count",
                    "totaltransct": "Total_Trans_Amt",
                    "totaltxnamt": "Total_Trans_Ct",
                    "trb": "Total_Revolving_Bal"
                    }, inplace = True)
        logger.info(f"RAW ADW DATA[1]:\n{dataset_all.head(1).to_json(orient='records')}")
        
        dataset_all = dataset_all.sample(frac=1).head(NUM_OF_DATA) if NUM_OF_DATA!=0 else dataset_all.sample(frac=1)
        return json.loads(dataset_all.to_json(orient="records"))

    def prepareAPIBody(self, testdata, globalParameters={"method": "predict"}):
        testBody = {"Inputs": {"data": testdata}, "GlobalParameters": globalParameters}

        return testBody

    def predictCustomerScore(self, adw_data):
        print("preparing api body...")
        # logger.info(f"PROCESSED ADW DATA:\n{adw_data}")
        logger.info("preparing api body...")
        api_body = self.prepareAPIBody(adw_data, globalParameters={"method": "predict"})

        inference_result, az_inference_time =  azure_churn_predict(api_body)
        return inference_result, az_inference_time

    def prepareMailBody(self, offer):
        try:
            htmlmsg = MIMEMultipart()
            htmlmsg["From"] = FROM_EMAIL
            htmlmsg["To"] = ", ".join(RECIPIENT)
            htmlmsg["Subject"] = CHURN_EMAILSUBJECT
            body = CHURN_EMAILBODY.replace("+{offer}+", offer)
            htmlmsg.attach(MIMEText(body, "html"))
            # print(body)
            mailobject = htmlmsg.as_string()
        except Exception as e:
            print("Error Creating Mail Body")
            logger.critical(f"[ERROR]: Error in Creating Mail Body: {e}")
            print(e)

        return mailobject

    def sendMail(self, mailobject):
        # logger.info(f"EMAIL BODY: {mailobject}")
        try:
            SSL_context = ssl.create_default_context()
            print("sending email now...")
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=EMAIL_TIMEOUT) as server:
                server.starttls(context=SSL_context)
                server.login(FROM_EMAIL, EMAILPASSWORD)
                server.sendmail(FROM_EMAIL, RECIPIENT, mailobject)
                print('EMAIL SENT!')
                server.quit()
        except Exception as e:
            logger.critical(f"[ERROR] CANNOT SEND MAIL: {e}")
            print("EMAIL SERVER ERROR!\n",e)

    def triggerMail(self,id, offer):
        print("triggering email...")
        try:
            logger.info(f"SENDING OFFER MAIL TO CUSTOMER {id} WITH OFFER {offer}")
            mailobject = self.prepareMailBody(offer)
            self.sendMail(mailobject)

        except Exception as e:
            print("[ERROR]: Trigger Mail", e)
            logger.critical(f"[ERROR]: CANNOT SEND MAIL: {e}")
            # return False
        
        return 0
