FROM python:3.10.2-slim

# qual usuário que nos teremos no container
RUN apt update && apt install -y --no-install-recommends \
    default-jre \
    git \
    curl \
    wget

RUN useradd -ms /bin/bash python

RUN pip install pdm

USER python

WORKDIR /home/python/app

ENV MY_PYTHON_PACKAGES=/home/python/app/__pypackages__/3.10
ENV PYTHONPATH=${PYTHONPATH}/home/python/app/src
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH $PATH:${MY_PYTHON_PACKAGES}/bin

RUN echo 'eval "$(pdm --pep582)"' >> ~/.bashrc

CMD [ ".docker/entrypoint.sh" ]
