import logging, colorlog, datetime, re, os

'''
Loggers：记录器，提供应用程序代码能直接使用的接口；

Handlers：处理器，将记录器产生的日志发送至目的地；

Filters：过滤器，提供更好的粒度控制，决定哪些日志会被输出；

Formatters：格式化器，设置日志内容的组成结构和消息字段。
        %(name)s Logger的名字         #也就是其中的.getLogger里的路径,或者我们用他的文件名看我们填什么
        %(levelno)s 数字形式的日志级别  #日志里面的打印的对象的级别
        %(levelname)s 文本形式的日志级别 #级别的名称
        %(pathname)s 调用日志输出函数的模块的完整路径名，可能没有
        %(filename)s 调用日志输出函数的模块的文件名
        %(module)s 调用日志输出函数的模块名
        %(funcName)s 调用日志输出函数的函数名
        %(lineno)d 调用日志输出函数的语句所在的代码行
        %(created)f 当前时间，用UNIX标准的表示时间的浮 点数表示
        %(relativeCreated)d 输出日志信息时的，自Logger创建以 来的毫秒数
        %(asctime)s 字符串形式的当前时间。默认格式是 “2003-07-08 16:49:45,896”。逗号后面的是毫秒
        %(thread)d 线程ID。可能没有
        %(threadName)s 线程名。可能没有
        %(process)d 进程ID。可能没有
        %(message)s用户输出的消息
'''




'''日志颜色配置'''
log_colors_config = {
    #颜色支持 blue蓝，green绿色，red红色，yellow黄色，cyan青色
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red,bg_white',
}

'''创建logger记录器'''
logger = logging.getLogger('my_logger')

# 输出到控制台
console_handler = logging.StreamHandler()

'''日志级别设置'''
log_level = os.getenv('LOG_LEVEL', 'INFO')
if log_level in ['DEBUG', 'INFO', 'WARNING']:
    level = getattr(logging, log_level)
else:
    level = getattr(logging, 'INFO')

logger.setLevel(level)
console_handler.setLevel(level)

# 输出到文件
log_export = os.getenv('LOG_EXPORT', 'False')
if log_export.lower() == 'true':
    path = os.getenv('LOG_PATH', '/var/tmp/emby_notifier_tg/')
    os.makedirs(path, exist_ok=True)  # This will create the directory if it does not exist, and do nothing if it does.
    '''Get the current date as the log file name'''
    fileName = datetime.datetime.now().strftime('%Y-%m-%d') + '.log'  # Use strftime to format the date
    file_handler = logging.FileHandler(filename=os.path.join(path, fileName), mode='a', encoding='utf8')
    # Set the minimum output level of the log saved to the file
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(filename)s|%(funcName)s|%(lineno)d] [%(levelname)s] : %(message)s',
        datefmt='%Y-%m-%d  %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)


#控制台的日志格式
console_formatter = colorlog.ColoredFormatter(
    #输出那些信息，时间，文件名，函数名等等
    fmt='[%(asctime)s] [%(filename)s|%(funcName)s|%(lineno)d] %(log_color)s[%(levelname)s]%(white)s : %(message)s',
    #时间格式
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors=log_colors_config
)
console_handler.setFormatter(console_formatter)

# 避免重复添加handler，导致日志重复输出
if not logger.handlers:
    logger.addHandler(console_handler)
    if log_export.lower() == 'true':
        logger.addHandler(file_handler)

console_handler.close()
if log_export.lower() == 'true':
    file_handler.close()



def SensitiveData(s, head=2, tail=4, mask='*****'):
    # 定义可能包含敏感信息的模式
    patterns = [
        r'\b\d{%d,}\b',  # 匹配连续的数字
        r'\b[A-Fa-f0-9]{40}\b',  # 匹配BTIH哈希
        r'\b[A-Fa-f0-9]{34}\b',  # 匹配MD5哈希 2 + 32 (passkey=xxxxxx, 等号被编码为 %3d, 因此需要加2个字符长度)
    ]

    # 对每个模式进行处理
    for pattern in patterns:
        if '%d' in pattern:
            pattern = pattern % (head + tail)
        s = re.sub(pattern, lambda m: m.group()[:head] + mask + m.group()[-tail:], s)

    return s