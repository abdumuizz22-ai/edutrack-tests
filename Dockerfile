FROM selenium/standalone-chrome:latest

USER root

RUN apt-get update && apt-get install -y python3 python3-pip --no-install-recommends \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install selenium==4.15.2 pytest==7.4.3 --break-system-packages

WORKDIR /tests

COPY . .

CMD ["python3", "-m", "pytest", "test_edutrack.py", "-v", "--tb=short"]
