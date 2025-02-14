ARG BUILD_FROM
FROM $BUILD_FROM

COPY main.py requirements.txt run.sh /

# Install requirements for add-on
RUN apk add --no-cache --update python3 python3-dev py3-pip py-pip 
RUN pip install --break-system-packages --no-cache-dir -r /requirements.txt

#CMD [ "python3", "/main.py" ]

# Copy data for add-on
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
