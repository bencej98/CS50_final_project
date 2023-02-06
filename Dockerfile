FROM python:3-alpine3.15
WORKDIR /CS50_final_project
COPY . /CS50_final_project
RUN pip install -r requirements.txt
EXPOSE 3000
CMD python ./app.py