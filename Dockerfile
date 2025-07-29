FROM pytorch/pytorch:2.7.1-cuda11.8-cudnn9-runtime
RUN apt update
RUN apt install -y git
ADD requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8000
WORKDIR /app
CMD ["bash"]