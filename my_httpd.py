from aiohttp import web
import asyncio
import log, media
import json, traceback
import my_utils


async def worker(msg_queue):
    log.logger.info("Emby Notifier started.")
    while True:
        msg = await msg_queue.get()  # 从队列中获取消息
        # 在这里进行消息处理，如发送到其他地方或执行其他操作
        # 仅支持 "Event": "library.new" 类型时间，其余不处理
        try:
            # 将unicode编码转换为中文字符
            if my_utils.contains_unicode_escape(msg):
                log.logger.debug("msg contains unicode escape sequences.")
                msg = msg.encode('utf-8').decode('unicode_escape')
            log.logger.debug(f"Decoded message: {msg}")
            media.process_media(msg)
        except Exception as e:
            log.logger.error(traceback.format_exc())


async def handle_post(request):
    # 从 POST 请求中读取数据
    data = await request.text()
    log.logger.debug(data)
    # check content-type
    if request.content_type != "application/json":
        log.logger.error(
            f"Unsupported content type: {request.content_type}, please check your webhooks setting, "
            + "and choose 'application/json' as request content type."
        )
    else:
        # 将数据放入队列
        await request.app["msg_queue"].put(data)

    # 返回 200 OK
    return web.Response()


async def my_httpd():
    # 创建消息队列
    msg_queue = asyncio.Queue()

    # 创建 aiohttp 应用，并将消息队列存储在应用对象中
    app = web.Application()
    app["msg_queue"] = msg_queue

    # 添加路由，自定义 post 处理函数
    app.router.add_post("/", handle_post)

    # 创建 worker 任务协程
    worker_task = asyncio.create_task(worker(msg_queue))

    # 运行 aiohttp 服务器
    runner = web.AppRunner(app)
    await runner.setup()
    # 使用 localhost:8000 无法监听本地网络地址，因此使用 0.0.0.0:8000 进行监听
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()
    log.logger.info("HTTP server started at http://localhost:8000")

    # 等待 worker 任务完成
    await worker_task
