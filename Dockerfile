FROM python:3-alpine3.15
WORKDIR /CS50_project
COPY . /CS50_project
RUN pip install -r requirements.txt
EXPOSE 3000
CMD python ./app.py