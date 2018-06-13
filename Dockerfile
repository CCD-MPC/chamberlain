# conclave-web image for openshift

FROM registry.access.redhat.com/rhel

WORKDIR /app

RUN curl --silent --location https://rpm.nodesource.com/setup_10.x | bash -

RUN yum -y update \
    && yum -y install git \
    && yum -y install nodejs \
    && yum -y install wget

RUN wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm \
    && rpm -ivh /app/epel-release-latest-7.noarch.rpm

RUN yum -y install epel-release \
    && yum -y install https://centos7.iuscommunity.org/ius-release.rpm \
    && yum -y install python35u python35u-pip


RUN pip3.5 install virtualenv

RUN cd /app \
    && git clone https://github.com/multiparty/conclave-web.git

RUN cd /app/conclave-web \
    && virtualenv backend/venv \
    && source backend/venv/bin/activate \
    && pip3.5 install -r requirements.txt

RUN cd /app/conclave-web/frontend \
    && npm run build

RUN cd /app/conclave-web

CMD ["gunicorn", "wsgi:app"]


