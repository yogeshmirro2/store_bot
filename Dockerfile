FROM python:3.9.7-slim-buster
WORKDIR .
RUN apt -qq update && apt -qq install -y git wget python3-dev
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["bash", "start.sh"]
