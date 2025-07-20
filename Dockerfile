FROM python:latest
RUN apt update
RUN apt install -y git
ADD requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8000
WORKDIR /app
CMD ["bash"]