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
    && yum -y install python-pip

RUN pip install virtualenv

RUN cd /app \
    && git clone https://github.com/multiparty/conclave-web.git

RUN cd /app/conclave-web \
    && source backend/venv/bin/activate

RUN cd /app/conclave-web/frontend \
    && npm run build

RUN cd /app

CMD ["gunicorn", "wsgi:app"]


