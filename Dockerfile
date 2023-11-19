FROM python:3

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY src/ src/

WORKDIR src

ENTRYPOINT ["python", "minted-api-request.py"]