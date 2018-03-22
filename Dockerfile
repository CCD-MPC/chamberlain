# Docker file for the simpledsapp

FROM fnndsc/ubuntu-python3:latest


ENV APPROOT="/tmp/conclave-web"  VERSION="0.1"

RUN mkdir ${APPROOT}
RUN mkdir ${APPROOT}/templates


COPY ["./app.py", "${APPROOT}"]
COPY ["./requirements.txt", "${APPROOT}"]
COPY ["templates", "${APPROOT}/templates/"]

WORKDIR $APPROOT

RUN pip install -r requirements.txt

CMD ["app.py"]