FROM python:3.10-slim
WORKDIR /code
COPY . /code
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 6379
ENV NAME World
CMD ["celery", "-A", "app.tasks", "worker", "--loglevel=info"]
