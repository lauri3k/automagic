FROM python:3.11-slim
RUN pip install requests
WORKDIR /root
COPY autograde.py .
COPY magic.py .
ENTRYPOINT [ "python", "autograde.py" ]