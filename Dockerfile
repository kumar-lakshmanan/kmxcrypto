FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir functions-framework
RUN pip install --no-cache-dir -r requirements.txt
ENV FUNCTION_TARGET=hello_http
EXPOSE 8080
CMD ["functions-framework", "--target=mymainfunction", "--port=8080"]