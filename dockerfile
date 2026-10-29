FROM python:3.11-alpine3.18

LABEL maintainer="Xu@nCh3n"

ENV TZ=Asia/Shanghai LANG=zh_CN.UTF-8 PYTHONUNBUFFERED=1

EXPOSE 8000

WORKDIR /usr/src/myapp

RUN python3 -m pip install --no-cache-dir requests colorlog aiohttp -q

COPY . .

ENTRYPOINT ["python3"]
CMD ["main.py"]
