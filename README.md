# python-chat
    server.py
        服务端文件，主进程中，创建图形化界面，询问地址（主机名，端口），点击开始进入聊天室。
        创建子进程，开始网络连接，使用select.select循环接收客户端连接请求，使用timeout不断检查与主进程间队列（multiprocessing.Queues）的情况
    client.py
        客户端文件，主进程中，创建图形化界面，询问地址（主机名，端口），点击开始以连接到客户端。
        创建子进程，开始网络连接。
    settings.py
        默认设置
