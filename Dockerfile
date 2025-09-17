FROM python:3.13-slim

WORKDIR /app

RUN pip install rembg[cpu,cli] && \
    rembg d silueta isnet-general-use isnet-anime

COPY . .

# 设置默认端口环境变量
ENV PORT=7001

EXPOSE $PORT

CMD ["sh", "-c", "python main.py -p $PORT"]