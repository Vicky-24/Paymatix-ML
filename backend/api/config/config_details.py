NUM_OF_DATA=500

SQLSERVER_DB_SERVER="managed-instance-paymatix.public.856aa56af2d6.database.windows.net,3342"
SQLSERVER_DB_DRIVER="{ODBC Driver 18 for SQL Server}"
SQLSERVER_DB_NAME="paymatix_proddb"
SQLSERVER_DB_USER="ADB_user"
SQLSERVER_DB_PASSWORD="@d8_MIDBpwd"

FROM_EMAIL='harvisbanking@gmail.com'
RECIPIENT = ['bhims2@hexaware.com', 'senthilkumarb4@hexaware.com' 'arunkumarl@hexaware.com', 'rajeshsankark@hexaware.com']  # , 'mohammadA1@hexaware.com', 'amansinghc@hexaware.com']
SMTP_PORT=587
SMTP_SERVER='smtp.gmail.com'
EMAILPASSWORD='rrnmymxqxfeznnwu'
EMAIL_TIMEOUT=300

CHURN_TABLE_NAME="churn"
CHURN_MODEL_ENDPOINT="https://bank-prac-churn-v2.centralindia.inference.ml.azure.com/score"
CHURN_DEPLOYMENT_NAME="churn"
CHURN_MODEL_API_KEY="of9D0WMm2WWjovzAcvC1shaMOeGzAabl"
CHURN_EMAILSUBJECT='New Offers for your Account'
CHURN_EMAILBODY="""\
    <html>
        <body>
            <div>Hi,</div><br>
            <div>You have received the following offer(s)!<br><br>
            +{offer}+
            </div><br><br><br>
            <div>Thanks & Regards,</div><br>
            <div>Hexaware Banking</div>
            <img src='cid:leftSideImage' style='float:left;width:20%;height:20%;'/>
        </body>
    </html>
"""

BUF_TABLE_NAME="CustomerTable"
TOLERANT_CUSTOMER_SCORE=37
BUF_MODEL_ENDPOINT="https://bank-prac-usecase.centralindia.inference.ml.azure.com/score"
BUF_DEPLOYMENT_NAME="bof-customertable-model"
BUF_MODEL_API_KEY="BbcTFh89FJ183TFkAsxxO5lWhPshOX0G"
BUF_EMAILSUBJECT='BUF PREDICTIONS REPORT'
BUF_EMAILBODY="""\
    <html>
    <body>
        <p>Hi,<br>
        Please find attached the list of customers deemed to have fraudulent transactions based on BUF predictions.\n\n
        </p>
        Thanks.
    </body>
    </html>
"""