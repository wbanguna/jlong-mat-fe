FROM python:3
RUN mkdir -p /opt/jlong-mat-fe
WORKDIR /opt/jlong-mat-fe/
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD sleep 10 && python ./main.py

