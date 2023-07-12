FROM python:3.8

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

WORKDIR /app

COPY pbf /app/pbf
COPY dockerrun.py /app/dockerrun.py

EXPOSE 1000

CMD ["python", "/app/dockerrun.py"]