FROM python:3.12
COPY ./dictionary/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY ./dictionary /app
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]