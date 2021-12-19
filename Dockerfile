# For more information, please refer to https://aka.ms/vscode-docker-python
FROM public.ecr.aws/bitnami/python:3.10

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install git
RUN apt-get update && apt-get install -y git

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

RUN groupadd -g 450 sws && useradd -s /bin/bash -u 5678 -g 450 appuser

COPY static /app/static
COPY config /app/config
COPY cdpb_test_orchestrator /app/cdpb_test_orchestrator
RUN chown -R appuser /app

USER appuser
WORKDIR /app

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python3", "-m", "cdpb_test_orchestrator"]
