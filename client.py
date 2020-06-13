#客户端代码

import sys
from time import sleep,ctime
from multiprocessing import Process,Queue
from socket import *
from setting import *
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox

def main_gui():
    #主窗口
    root=Tk()

    #设置窗口居中
    center(root,300,200)

    #设置窗口其他属性
    root.title("多人聊天室窗口")
    root.resizable(0,0)
    root.configure(bg="white")
    # root.iconbitmap("python.ico")

    #添加主机名（HOST)以及端口号(POST)等输入框
    pad=10
    Label(root,text="主机名(HOST):").grid(row=0,column=0,padx=pad,pady=pad)
    ent_host=Entry(root)
    ent_host.insert(0,HOST)
    ent_host.grid(row=0,column=1,padx=pad,pady=pad)
    Label(root,text="端口号(Port):").grid(row=1,column=0,padx=pad,pady=pad)
    ent_port = Entry(root)
    ent_port.insert(0, PORT)
    ent_port.grid(row=1, column=1, padx=pad, pady=pad)
    Label(root, text="用户名（User）：").grid(row=2, column=0, padx=pad, pady=pad)
    ent_user = Entry(root)
    ent_user.grid(row=2, column=1, padx=pad, pady=pad)
    ent_user.focus_set()

    # 组件列表
    widgets = {
        "ent_host": ent_host,
        "ent_port": ent_port,
        "ent_user": ent_user
    }

    # 添加确认按钮
    btn_cfm = Button(root, text="加入目标聊天室", command=lambda: validate(root, widgets))
    btn_cfm.grid(rowspan=2, columnspan=2, padx=pad, pady=pad)

    # 绑定事件
    root.bind("<Return>", lambda event: validate(root, widgets))

    # 主循环事件
    root.mainloop()


def validate(root, widgets):
    # 确认按钮事件，检查是否输入有误
    host, port, user = widgets["ent_host"].get(), widgets["ent_port"].get(), widgets["ent_user"].get()

    # 如果端口号不是纯数字
    try:
        port = int(port)
    except:
        messagebox.showerror("错误", "端口号必须为数字！")
        return

        # 弹出错误窗口
    if not host or not port or not user:
        messagebox.showerror("错误", "主机名或端口或用户名不可为空！")
        return

    # 有效地址
    addr = (host, port)

    # 检查是否套接字成功
    try:
        client = socket(AF_INET, SOCK_STREAM)
        client.connect(addr)
    except Exception as e:
        messagebox.showerror("错误", f"无法在{addr}上生成套接字！")
        print(e)
        return
    else:
        # 生成两个队列
        # queue负责在子进程中循环get主进程的信息
        # queueu负责在父进程中循环get子进程的消息
        queue = Queue()
        queueu = Queue()

        # 发送成功建立连接信息
        client.send(bytes(f"{user}进入了聊天室。\n", "UTF-8"))

        # 生成子进程
        process = Process(target=inet, args=(client, queue, queueu, user))
        process.daemon = True
        process.start()

        # 创建聊天室页面
        chatroom_gui(root, queue, queueu, user)


def chatroom_gui(r, queue, queueu, user):
    # 聊天室页面
    r.destroy()
    root = Tk()

    # 设置窗口居中
    center(root, 500, 500)

    # 最小化窗口
    root.minsize(350, 350)

    # 菜单栏
    menubar = Menu(root)
    menubar.add_command(label="信息", command=None)
    menubar.add_command(label="退出", command=root.destroy)
    root.config(menu=menubar)

    # 文本框
    text = ScrolledText(root)
    text.pack(fill=BOTH)

    # 输入框
    ent = Entry(root, bg='gray', bd=3)
    ent.pack(fill=BOTH, side=BOTTOM)
    ent.focus_set()

    # 绑定事件
    root.bind("<Return>", lambda event: send(ent, queue, user))

    # 设置窗口其他属性
    root.title(f"多人聊天室 - {user}")
    root.configure(bg="white")
    # root.iconbitmap("python.ico")

    # 设置退出方法
    root.protocol("WM_DELETE_WINDOW", lambda: exit(root, queue, user))

    # 主循环函数
    root.after(1000, recv, root, queueu, text)


def exit(root, queue, user):
    data = user + "退出了聊天室。\n"
    queue.put(data)
    sleep(1)
    root.destroy()
    sys.exit(0)


def recv(root, queueu, text):
    if not queueu.empty():
        data = queueu.get()
        if data == 404:
            messagebox.showerror("错误", "服务端关闭了连接！")
            sys.exit(0)
        text.insert(END, data)
    root.after(1000, recv, root, queueu, text)


def send(ent, queue, user):
    now = ":".join(ctime().split()[3].split(":"))
    data = "[" + now + "] " + user + "：" + ent.get() + "\n"
    queue.put(data)
    ent.delete(0, END)


def inet(client, queue, queueu, user):
    # 子进程
    client.setblocking(0)
    while True:
        if not queue.empty():
            data = queue.get()
            if data:
                data = bytes(data, "UTF-8")
                client.send(data)
        try:
            data = client.recv(1024)
        except BlockingIOError as e:
            continue
        except:
            queueu.put(404)
        else:
            data = data.decode()
            queueu.put(data)


def main():
    # 主进程
    main_gui()


if __name__ == "__main__":
    main()