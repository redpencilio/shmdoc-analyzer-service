FROM mikidi/mu-python-template:python3-port
RUN cd /app && pip3 install -r requirements.txt
