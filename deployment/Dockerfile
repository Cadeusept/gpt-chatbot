FROM python:3.12-alpine
LABEL authors="cadeusept"

WORKDIR /app

COPY ../deployment/init/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ../ /app/

ENV PYTHONPATH=/app
CMD ["python", "cmd/integrator_main.py"]