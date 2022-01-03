FROM python:alpine
COPY . /app
WORKDIR /app
EXPOSE 5000
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
CMD python3 run.py
