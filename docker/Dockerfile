FROM ubuntu:focal

RUN apt-get update -y && \
    apt-get install software-properties-common -y

# Install python3
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update -y && \
    apt-get install python3.8 python3-pip -y

# Install quantum-robot
WORKDIR /quantum-robot
COPY . /quantum-robot
RUN pip install /quantum-robot

CMD [ "/bin/bash" ]