from Tkinter import *
from ctypes import *                                                                                                            
import sys
import tkFileDialog
from tkFileDialog import askopenfilename 

PAGE_READWRITE     =     0x04
KERNEL32 = windll.kernel32                                                
PAGE_EXECUTE_READWRITE = 0x00000040
MEMORIA_VIRTUAL = (0x1000 | 0x2000)
DELETE = 0x00010000
READ_CONTROL = 0x00020000
SYNCHRONIZE = 0x00100000
WRITE_DAC  = 0x00040000
WRITE_OWNER  = 0x00080000
TODAS_PERMISSOES = (DELETE | READ_CONTROL | SYNCHRONIZE | WRITE_DAC | WRITE_OWNER | 0xFFF)                                                                                                         


def Creditos():
    os.system('color a')
    print(menu)


def Open_channel():
    webbrowser.open('https://www.youtube.com/AdrielFreud')


def Github():
    webbrowser.open('https://github.com/AdrielFreud')



def Exit():
    sys.exit()
    exit()

def inject_code(shellcode, pid):

    print('[*] Abrindo o processo: %s' % pid)
    processo = KERNEL32.OpenProcess(TODAS_PERMISSOES, False, int(pid))

    if not processo:
            print('[-] Erro ao abrir processo')
            return False

    print('[*] Alocando memoria para o shellcode')
    shellcode_endereco = KERNEL32.VirtualAllocEx(processo, 0, len(shellcode), MEMORIA_VIRTUAL, PAGE_EXECUTE_READWRITE)

    print('[*] Escrevendo shellcode na memoria')
    bytes_escritos = c_int(0)
    KERNEL32.WriteProcessMemory(processo, shellcode_endereco, shellcode, len(shellcode), byref(bytes_escritos))

    print('[*] Criando nova thread')
    thread_id = c_ulong(0)
    if not KERNEL32.CreateRemoteThread(processo, None, 0, shellcode_endereco, None, 0, byref(thread_id)):
            return False

    print('[+] Injecao realizada com sucesso!')
    return True

def inject_dll(pid, dll_path):
    dll_len = len(dll_path)
    h_process = KERNEL32.OpenProcess(TODAS_PERMISSOES, False, int(pid))

    if not h_process:
        print("[*] Couldn't acquire a handle to PID: %s"%pid)

    arg_address = KERNEL32.VirtualAllocEx(h_process, 0, dll_len, MEMORIA_VIRTUAL, PAGE_READWRITE)
    written = c_int(0)
    KERNEL32.WriteProcessMemory(h_process, arg_address, dll_path, dll_len, byref(written))
    h_kernel32 = KERNEL32.GetModuleHandleA("kernel32.dll")
    h_loadlib  = KERNEL32.GetProcAddress(h_kernel32,"LoadLibraryA")
    thread_id = c_ulong(0)

    if not KERNEL32.CreateRemoteThread(h_process, None, 0, h_loadlib, arg_address, 0, byref(thread_id)):
        print("[*] Failed to inject the DLL. Exiting.")
    print("[*] Remote thread with ID 0x%08x created."%thread_id.value)

                                                                                        
class Application:
    dll_path = 0

    def __init__(self, master):

        self.master = master
        master.title('[ Injector ]')
        master['bg'] = "black"
        menubar = Menu(master)
        master.config(menu=menubar)
        filemenu = Menu(menubar)
        menubar.add_cascade(label='Menu', menu=filemenu)
        filemenu.add_command(label='Creditos', command=Creditos)
        filemenu.add_command(label='Canal', command=Open_channel)
        filemenu.add_command(label='Github', command=Github)
        filemenu.add_command(label='Exit', command=Exit)

        self.dll_label = Label(master, text="Procure sua DLL Abaixo!", bg="black", fg="Grey", font="Arial 12").place(x=10, y=10)
        self.dll_button = Button(master, text="Open", command=self.open_dll, bg="grey", width=20).place(x=23,y=50)

        self.lb = Label(master, text="=====================", fg="green", bg="black").place(x=10, y=100)

        self.code_label = Label(master, text="Insira seu Code!", bg="black", fg="Grey", font="Arial 12").place(x=35, y=130)
        self.code_entry = Entry(master, width=25)
        self.code_entry.place(x=20,y=170)

        self.injetar = Button(master, text="Injetar", bg="gray", command=self.inserir).place(x=23, y=250)
        self.label_pid = Label(master, text="PID:", bg="black", fg="grey").place(x=100, y=255)
        self.get_pid = Entry(master, width=5)
        self.get_pid.place(x=130, y=255)

        self.creditos = Label(master, text="Creditos: Adriel Freud", bg="black", fg="green", font="Arial 10").place(x=30, y=200)

    def open_dll(self):
        filename = askopenfilename(filetypes=[("Dll files","*.dll")])
        if filename:
            self.dll_path = filename.replace('/', "\\")

    def inserir(self):

        if self.dll_path:
            inject_dll(int(self.get_pid.get()), self.dll_path)

        elif self.code_entry:
            self.dll_path = 0
            inject_code(str(self.code_entry.get()), int(self.get_pid.get()))

        self.dll_path = 0
        self.code_entry = 0

root = Tk()
my_gui = Application(root)
root.geometry("200x300")
root.mainloop()
