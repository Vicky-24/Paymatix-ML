FROM ubuntu:20.04

WORKDIR /workdir_bof

RUN apt-get update

RUN apt-get install -y python3
RUN apt-get install python3-pip -y
RUN apt-get -y install gcc gnupg2 \
    && pip install pyodbc

RUN apt-get install -y lsb-release && apt-get clean all \
    && echo $(lsb_release -rs)\
    && apt -y install curl\
    && apt-get install -y unixodbc-dev\
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -\
    && curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list\
    && apt-get update\
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18\
    && apt-get install -y unixodbc-dev

COPY . .
RUN pip3 install -r requirements.txt
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8990"]
# CMD ["uvicorn", "main:app", "--port=8990"]