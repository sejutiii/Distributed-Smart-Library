FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/ 
COPY .env .
# Need to modify the IP in the .env file to the network IP
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
# docker build -t user-service:v4 .
# docker run -d -p 8081:8081 --name user-service user-service:v4