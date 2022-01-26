FROM python
RUN pip install requests
WORKDIR /root
COPY autograde.py .
COPY magic.py .
ENTRYPOINT [ "python", "autograde.py" ]