#FROM 123.56.140.4:808/cfd/cfd_python10:v1
FROM 123.56.140.4:808/cfd/cfd_python:v1
RUN rm -rf /code/server
COPY ./server /server
