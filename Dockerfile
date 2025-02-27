FROM ubuntu:latest
LABEL authors="BARUX"

ENTRYPOINT ["top", "-b"]