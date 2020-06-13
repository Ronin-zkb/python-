#服务器端

from time import ctime
from multiprocessing import Process,Queue
from select import select
from socket import *
from setting import *
from tkinter import *
from tkinter.scrolledtext import  ScrolledText
from tkinter import messagebox

def main_gui():
    #设置主窗口
    root=Tk()
    #设置窗口其他属性
    root.title("多人聊天室主窗口")
    root.resizable(0,0)
    root.configure(bg="white")
    #root.iconbitmap("python.ico")

    #添加主机名（HOST)以及端口号（PORT)等输入框

    pad=10
    Label(root,text="主机名(HOST):").grid(row=0,column=0,padx=pad,pady=pad)
    ent_host=Entry(root)
    ent_host.insert(0,HOST)
    ent_host.grid(row=0,column=1,padx=pad,pady=pad)
    Label(root,text="端口号(Port):").grid(row=1,column=0,padx=pad,pady=pad)
    ent_port=Entry(root)
    ent_port.insert(0,PORT)
    ent_port.grid(row=1,column=1,padx=pad,pady=pad)


    #组件列表
    widgets={
        "ent_host":ent_host,
        "ent_port":ent_port
    }

    #添加确认按钮
    btn_cfm=Button(root,text="新建网络聊天室",command=lambda:validate(root,widgets))
    btn_cfm.grid(rowspan=2,columnspan=2,padx=pad,pady=pad)


    #绑定事件
    root.bind("<Return>",lambda event:validate(root,widgets))

    #主循环事件
    root.mainloop()

def validate(root,widgets):
    #确认按钮事件，检查是否输入有误
    host,port=widgets["ent_host"].get().widgets["ent_port"].get()

    #如果端口号不是纯数字
    try:
        port=int(port)
    except:
        messagebox.showerror("错误","端口号必须为数字！")
        return

    #弹出错误窗口
    if not host or not port:
        messagebox.showerror("错误","主机名或端口不可为空!")
        return

    #有效地址
    addr=(host,port)

    #检查是否套接字成功
    try:
        server=socket(AF_INET,SOCK_STREAM)
        server.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        server.bind(addr)
        server.listen(10)
    except Exception as e:
        messagebox.showerror("错误",f"无法在{addr}上生成套接字！")
        print(e)
        return
    else:
        #生成两个队列
        #queue负责在子进程中循环get主进程的信息
        #queueu负责在父进程中循环get子进程的消息
        queue=Queue()
        queueu=Queue()

        #生成子进程
        process=Process(target=inet,args=(server,queue,queueu))
        process.daemon=True
        process.start()

        #创建聊天室页面
        chatroom_gui(root,queue,queueu)

def chatroom_gui(r,queue,queueu):
    #聊天室页面
    r.destroy()
    root=Tk()

    #设置窗口居中
    center(root,500,500)

    #最小化窗口
    root.minsize(350,350)

    #菜单栏
    menubar=Menu(root)
    menubar.add_command(label="新建",command=None)
    menubar.add_command(label="信息", command=None)
    menubar.add_command(label="退出", command=root.destroy)
    root.config(menu=menubar)

    #文本框
    text=ScrolledText(root)
    text.pack(fill=BOTH)

    #输入框
    ent=Entry(root,bg='gray',bd=3)
    ent.pack(fill=BOTH,side=BOTTOM)
    ent.focus_set()


    #绑定事件
    root.bind("<Return>",lambda event:send(ent,queue,text))

    #设置窗口其他属性
    root.title("多人聊天室-管理员")
    root.configure(bg="white")
    root.iconbitmap('python.ico')

    #主循环函数
    root.after(1000,recv,root,queueu,text)


def recv(root,queueu,text):
    if not queueu.empty():
        data=queueu.get()
        text.insert(END,data)
    root.after(1000,recv,root,queueu,text)

def send(ent,queue,text):
    now=":".join(ctime().split()[3].split(":"))
    data="["+now+"]"+"管理员："+ent.get()+"\n"
    queue.put(data)
    text.insert(END,data)
    ent.delete(0,END)

def inet(server,queue,queueu):
    #子进程
    rlist=[server]
    wlist=[]
    xlist=[]

    while True:
        #接受队列信息
        if not queue.empty():
            data=queue.get()
            for conn in rlist:
                if conn is not server:
                    conn.send(bytes(data,"UTF-8"))
        rs,ws,xs=select(rlist,wlist,l)

        for r in rs:
            if r is server:
                conn,addr=r.accept()
                rlist.append(conn)
            else:
                try:
                    data=r.recv(1024)
                except:
                    rlist.remove(r)
                else:
                    queueu.put(data.decode())
                    for conn in rlist:
                        if conn is not server:
                            conn.send(data)

def main():
    #主进程
    main_gui()

if __name__=="__main__":
    main()



