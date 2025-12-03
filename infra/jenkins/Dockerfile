FROM jenkins/jenkins:lts

USER root

# Install Python 3.11 and tools
RUN apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-dev && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

# Install pip
RUN apt-get install -y python3-pip && \
    python3.11 -m pip install --upgrade pip setuptools wheel

USER jenkins
USER jenkins
