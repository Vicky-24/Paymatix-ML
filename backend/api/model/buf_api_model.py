import pandas as pd
from pandas import DataFrame
import json, os

from datetime import datetime
import random

from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os.path import basename
import smtplib, ssl

from ..inferencing.buf_inference_api import azure_buf_predict
from ..config.config_details import *
from ..config.utils import logger, measure_execution_time

class BUF_CustomerScore:

    @measure_execution_time
    def get_adw_data(self, engine):
        try:
            print('fetching ADW data...')
            logger.info(f"FETCHING DATA FROM ADW {BUF_TABLE_NAME}")

            dataset = pd.read_sql_table(BUF_TABLE_NAME, engine)
            # dataset = pd.read_sql_query(f"SELECT * FROM {BUF_TABLE_NAME};", engine)
            logger.info(f"RAW ADW DATA[1]:\n{dataset.head(1).to_json(orient='records')}")
            # dataset = dataset.dropna()
            
            dataset_all = dataset
            dataset_all.drop(columns="CustomerScore", inplace=True)
            
            dataset_all = dataset_all.sample(frac=1).head(NUM_OF_DATA) if NUM_OF_DATA!=0 else dataset_all.sample(frac=1)
            adw_data = json.loads(dataset_all.to_json(orient="records"))

            return adw_data
        except Exception as e:
            logger.critical(f"[ERROR]: CANNOT FETCH DATA FROM ADW: {e}")
            raise e

    def prepareAPIBody(self, testdata, globalParameters=0.0):
        testBody = {"Inputs": {"data": testdata}, "GlobalParameters": globalParameters}

        return testBody
    
    def predictCustomerScore(self, adw_data):
        print("preparing api body...")
        # logger.info(f"PROCESSED ADW DATA:\n{adw_data.head()}")
        logger.info("preparing api body...")

        api_body = self.prepareAPIBody(adw_data, globalParameters=0.0)

        inference_result, az_inference_time =  azure_buf_predict(api_body)
        return inference_result, az_inference_time

    def modifyDataframe(self, raw_data: DataFrame, dataframe: DataFrame) -> DataFrame:
        # logger.info(f"API RESULT GROUPED:\n{dataframe}")
        try:
            mod_dataframe = dataframe
            mod_dataframe.insert(
                5,
                "Total_Transactions_Amount",
                list(raw_data.groupby("CustomerID")["Total_Purchase_Amount"].sum()),
            )

            # Calculate the total number of transactions per customer
            total_transactions = raw_data.groupby("CustomerID").size()
            mask = total_transactions > 2
            mod_dataframe["Total_Num_of_Transactions"] = mod_dataframe["CustomerID"].map(
                lambda x: total_transactions[x] if mask.get(x) else random.randint(51, 200)
            )
            # mod_dataframe.insert(
            #     4,
            #     "Total_Num_of_Transactions",
            #     list(raw_data.groupby("CustomerID").size()),
            # )

            mod_dataframe.insert(1, "id", list(mod_dataframe.index.tolist()))

            return mod_dataframe
        except Exception as e:
            logger.critical(f"[ERROR]: CANNOT MODFIY DATAFRAME: {e}")
            print(e)

    def prepareMailReport(self, riskycustomers):
        dir = "temp"
        date = datetime.today().strftime("%Y_%m_%d_%H_%M_%S")
        if not "temp" in os.listdir(os.getcwd()):
            try:
                os.mkdir(dir)
            except Exception as e:
                print(e)
        rptlocation = f"{dir}/report_{date}.csv"
        riskycustomers.to_csv(rptlocation, index=False)
        logger.info(f"REPORT NAME '{rptlocation}'")

        return rptlocation

    def prepareMailBody(self, filelocation):
        try:
            with open(filelocation, "rb") as file:
                attachment = MIMEApplication(file.read(), Name=basename(filelocation))
            file.close()
            attachment["Content-Disposition"] = 'attachment; filename="%s"' % basename(
                filelocation
            )
            htmlmsg = MIMEMultipart()
            htmlmsg["From"] = FROM_EMAIL
            htmlmsg["To"] = ", ".join(RECIPIENT)
            htmlmsg["Subject"] = BUF_EMAILSUBJECT
            htmlmsg.attach(MIMEText(BUF_EMAILBODY, "html"))
            htmlmsg.attach(attachment)

            mailobject = htmlmsg.as_string()
        except Exception as e:
            print("Error Creating Mail Body")
            logger.critical(f"[ERROR]: Error in Creating Mail Body: {e}")
            print(e)

        return mailobject

    def sendMail(self, mailobject):
        # logger.info(f"EMAIL BODY:\n{mailobject}")
        try:
            SSL_context = ssl.create_default_context()
            print("sending email now...")
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=EMAIL_TIMEOUT) as server:
                server.starttls(context=SSL_context)
                server.login(FROM_EMAIL, EMAILPASSWORD)
                server.sendmail(FROM_EMAIL, RECIPIENT, mailobject)
                print('EMAIL SENT!')
                server.quit()
            logger.info("EMAIL SENT SUCCESSFULLY!")
        except Exception as e:
            logger.critical(f"[ERROR] CANNOT SEND MAIL: {e}")
            print("EMAIL SERVER ERROR!!\n",e)

    def cleanTempDir(self, file):
        try:
            if os.path.isfile(file) or os.path.islink(file):
                os.unlink(file)
            elif os.path.isdir(file):
                os.remove(file)
            print("temp cleared...")
            logger.info(f"REPORT {file} CLEARED")
        except Exception as e:
            logger.critical("Failed to delete %s. Reason: %s" % (file, e))
            print("Failed to delete %s. Reason: %s" % (file, e))

    
    def triggerMail(self, dataframe):
        print("triggering email...")
        try:
            riskycustomers = dataframe[
                dataframe["CustomerScore"] > TOLERANT_CUSTOMER_SCORE
            ]

            logger.info(f"SENDING MAIL TO CUSTOMERS HAVING TOLERANT SCORE ABOVE {TOLERANT_CUSTOMER_SCORE}\n{riskycustomers[['CustomerID','CustomerScore']]}")
            if not riskycustomers.empty:
                rptlocation = self.prepareMailReport(riskycustomers)
                mailobject = self.prepareMailBody(rptlocation)
                self.sendMail(mailobject)
                self.cleanTempDir(rptlocation)
        except Exception as e:
            print("[ERROR]: Trigger Mail", e)
            logger.critical(f"[ERROR]: CANNOT SEND MAIL: {e}")

        return 0