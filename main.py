import os
import sys
import time
import json
import shutil
import ctypes
import pygments
import subprocess
import webbrowser
from tkinter import *
from tkinter.font import Font
from tklinenums import TkLineNumbers
from pygments.lexers import PythonLexer
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfile, asksaveasfile

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
elif __file__:
    application_path = os.path.dirname(__file__)

root = Tk()
root.title("Python Compiler")
root.iconbitmap(default=os.path.join(application_path, 'favicon.ico'))
root.geometry("1100x850")
root.resizable(False, False)

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

VERSION = "1.1.0"
VERSION_TEXT = "v1.1.0"
TEMP_FOLDER_PATH = os.path.join(application_path, ".codedumps")

def br(master=root):
    Label(master, text="").pack()

def openFile(*_):
    filetypes = [
        ('Python Files', '*.py'),
        ('Text Files', '*.txt')
    ]
    file = askopenfile("r", filetypes=filetypes)
    if file:
        CODE.delete(1.0, END)
        CODE.insert(INSERT, file.read())
        highlightCode()
        update_highlighter()

def saveFile(*_):
    filetypes = [
        ('Python Files', '.py')
    ]
    file = asksaveasfile("w", filetypes=filetypes, defaultextension=".py")
    if file:
        file.write(CODE.get(1.0, END))
        file.close()

def newFile(*_):
    subprocess.Popen([sys.executable, f"{application_path}/main.py"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

def highlightCode(*_):
    linenums.redraw()
    for tag in CODE.tag_names(index=None):
        if tag != "sel":
            CODE.tag_remove(tag, "1.0", "end")

    for line in range(int(CODE.index(END).split(".")[0])):
        if line is None:
            line = int(CODE.index("insert").split(".")[0])
        line_text = CODE.get(f"{line}.0", f"{line}.end")
        start = f"{line}.0"

        for tag in CODE.tag_names(index=None):
            if tag != "sel":
                CODE.tag_remove(tag, f"{line}.0", f"{line}.end")

        for token, content in pygments.lex(line_text, PythonLexer()):
            end = f"{start.split('.')[0]}.{int(start.split('.')[1]) + len(content)}"
            CODE.tag_add(str(token), start, end)
            start = end

def generate_font_list(input_dict: dict) -> list:
    _font = Font(font=("Cooper", 18))
    font_dict = {"-family": _font.actual("family"), "-size": _font.actual("size")}

    for style_key, style_value in input_dict.items():
        if style_key == "family":
            font_dict["-family"] = style_value
        elif style_key == "size":
            font_dict["-size"] = style_value
        elif style_key == "bold":
            font_dict["-weight"] = "bold" if style_value else "normal"
        elif style_key == "italic":
            font_dict["-slant"] = "italic" if style_value else "roman"
        elif style_key == "underline":
            font_dict["-underline"] = style_value
        elif style_key == "strikethrough":
            font_dict["-overstrike"] = style_value

    font_list = []
    for x, y in zip(font_dict.keys(), font_dict.values()):
        font_list.extend([x, y])

    return font_list

def update_highlighter(highlighter: str="mariana") -> None:
    highlight_file = highlighter

    if highlighter in [
        x.split(".")[0] for x in os.listdir(os.path.join(application_path, "schemes"))
    ]:
        highlight_file = os.path.join(
            application_path, "schemes", highlighter + ".json"
        )
    try:
        with open(highlight_file) as file:
            CODE.configuration = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Style configuration file not found: '{highlight_file}'"
        )

    general_props = CODE.configuration.pop("general")
    selection_props = CODE.configuration.pop("selection")
    syntax_props = CODE.configuration.pop("syntax")

    CODE.config(**general_props)
    CODE.tag_configure("sel", **selection_props)

    for key, value in syntax_props.items():
        if isinstance(value, str):
            CODE.tag_configure(key, foreground=value)
        else:
            if "font" in value:
                value["font"] = generate_font_list(value["font"])
            CODE.tag_configure(key, **value)

def paste(*_):
    if CODE.tag_ranges("sel"):
        sel_start = CODE.index("sel.first")
        CODE.delete(sel_start, CODE.index("sel.last"))
        CODE.mark_set("insert", sel_start)

    try:
        CODE.insert(INSERT, root.clipboard_get())
    except:
        pass

    return "break"

def copy(*_):
    if CODE.tag_ranges("sel"):
        code = CODE.get(CODE.index("sel.first"), CODE.index("sel.last"))
    else:
        code = CODE.get(1.0, END)
    root.clipboard_clear()
    root.clipboard_append(code)
    root.update()
    return "break"

def cut(*_):
    if CODE.tag_ranges("sel"):
        sel_start = CODE.index("sel.first")
        sel_end = CODE.index("sel.last")
        code = CODE.get(sel_start, sel_end)
        del_start, del_end = sel_start, sel_end
    else:
        code = CODE.get(1.0, END)
        del_start, del_end = 1.0, END
    root.clipboard_clear()
    root.clipboard_append(code)
    root.update()
    CODE.delete(del_start, del_end)

    highlightCode()
    update_highlighter()

    return "break"

def selectAll(*_):
    CODE.tag_add(SEL, "1.0", END)
    CODE.mark_set(INSERT, "1.0")
    CODE.see(INSERT)

    return "break"

def undo(*_):
    try:
        CODE.edit_undo()
        highlightCode()
        update_highlighter()
    except:
        pass

    return "break"

def redo(*_):
    try:
        CODE.edit_redo()
        highlightCode()
        update_highlighter()
    except:
        pass

    return "break"

def compile_nd_run():
    code = CODE.get(1.0, END)
    input = INPUT.get(1.0, END)
    suid = str(time.time()).replace('.', '')

    if not os.path.isdir(TEMP_FOLDER_PATH):
        os.mkdir(TEMP_FOLDER_PATH)

    USER_FOLDER = os.path.join(application_path, suid)
    os.mkdir(USER_FOLDER)

    with open(f"{USER_FOLDER}\\code.py", "w") as code_file:
        code_file.write(code)
        code_file.close()

    with open(f"{USER_FOLDER}\\input.txt", "w") as input_file:
        input_file.write(input)
        input_file.close()

    result = subprocess.run(["python", f"{USER_FOLDER}\\code.py", "<", f"{USER_FOLDER}\\input.txt"], shell=True, capture_output=True, text=True)
    OUTPUT.config(state='normal')
    OUTPUT.delete(1.0, END)
    if result.stderr:
        OUTPUT.config(fg='Red')
        OUTPUT.insert(INSERT, result.stderr)
    else:
        OUTPUT.config(fg="Green")
        OUTPUT.insert(INSERT, result.stdout)
    OUTPUT.config(state='disabled')

    if os.path.exists(f"{USER_FOLDER}") and os.path.isdir(f"{USER_FOLDER}"):
        shutil.rmtree(f"{USER_FOLDER}")

Label(root, text="Python Compiler", fg="Blue", font=("Cooper Black", 45)).pack()

br()

APP_FRAME = Frame(root)

CODE_FRAME = Frame(APP_FRAME)
Label(CODE_FRAME, text="Enter your python code below.", fg="Black", font=("Cooper Black", 20), justify=CENTER).pack()

CODE_BLOCK_FRAME = Frame(CODE_FRAME)
CODE = ScrolledText(CODE_BLOCK_FRAME, undo=True, height=9, width=45, font=("Cooper", 18))

linenums = TkLineNumbers(CODE_BLOCK_FRAME, CODE, height=9, width=2, justify=CENTER)
linenums.pack(side=LEFT, fill=Y, expand=True)

CODE.pack()
CODE.bind("<KeyRelease>", highlightCode, add=True)
CODE.bind("<<Cut>>", cut, add=True)
CODE.bind("<<Copy>>", copy, add=True)
CODE.bind("<<Paste>>", paste, add=True)
CODE.bind("<Control-Key-a>", selectAll, add=True)
CODE.bind("<Control-Key-A>", selectAll, add=True)
CODE.bind("<Control-Key-s>", saveFile, add=True)
CODE.bind("<Control-Key-S>", saveFile, add=True)
CODE.bind("<Control-Key-n>", newFile, add=True)
CODE.bind("<Control-Key-N>", newFile, add=True)
CODE.bind("<Control-Key-o>", openFile, add=True)
CODE.bind("<Control-Key-O>", openFile, add=True)
CODE.bind("<Control-Key-z>", undo, add=True)
CODE.bind("<Control-Key-Z>", undo, add=True)
CODE.bind("<Control-Shift-Key-z>", redo, add=True)
CODE.bind("<Control-Shift-Key-Z>", redo, add=True)
root.bind("<Alt-Key-F4>", lambda *_: root.destroy())
root.bind("<Control-Key-w>", lambda *_: root.destroy())
root.bind("<Control-Key-W>", lambda *_: root.destroy())

highlightCode()
update_highlighter()

CODE.focus_set()
CODE_BLOCK_FRAME.pack()
CODE_FRAME.pack()

br(APP_FRAME)

INPUT_ND_OUTPUT_FRAME = Frame(APP_FRAME)

INPUT_FRAME = Frame(INPUT_ND_OUTPUT_FRAME)
Label(INPUT_FRAME, text="Input", font=("Cooper Black", 20)).pack()
INPUT = ScrolledText(INPUT_FRAME, undo=True, height=9, width=40, font=("Cooper", 18))
INPUT.pack()
INPUT_FRAME.pack(side=LEFT, padx=10)

OUTPUT_FRAME = Frame(INPUT_ND_OUTPUT_FRAME)
Label(OUTPUT_FRAME, text="Output", font=("Cooper Black", 20)).pack()
OUTPUT = ScrolledText(OUTPUT_FRAME, height=10, width=40, font=("Cooper", 16), state="disabled")
OUTPUT.pack()
OUTPUT_FRAME.pack(side=LEFT, padx=10)

INPUT_ND_OUTPUT_FRAME.pack()

br(APP_FRAME)

COMPILE_BTN = Button(APP_FRAME, text="Compile & Run", font=("Cooper Black", 20), command=compile_nd_run)

if sys.platform == "darwin" and COMPILE_BTN['command']:
    COMPILE_BTN.configure(cursor="pointinghand")
elif sys.platform.startswith("win") and COMPILE_BTN['command']:
    COMPILE_BTN.configure(cursor="hand2")

COMPILE_BTN.pack()

APP_FRAME.pack()

menubar = Menu(root)

file = Menu(menubar, tearoff = 0, font=("Cooper", 11))
menubar.add_cascade(label="File", menu=file)
file.add_command(label=f"New File{' '*4}(Ctrl+N)", command=newFile)
file.add_command(label=f"Open...{' '*6}(Ctrl+O)", command=openFile)
file.add_command(label=f"Save{' '*10}(Ctrl+S)", command=saveFile)
file.add_separator()
file.add_command(label=f"Exit{' '*12}(Ctrl+W)", command=root.destroy)

edit = Menu(menubar, tearoff = 0, font=("Cooper", 11))
menubar.add_cascade(label="Edit", menu=edit)
edit.add_command(label=f"Undo{' '*11}(Ctrl+Z)", command=undo)
edit.add_command(label=f"Redo{' '*11}(Ctrl+Shift+Z)", command=redo)
edit.add_separator()
edit.add_command(label=f"Cut{' '*14}(Ctrl+X)", command=cut)
edit.add_command(label=f"Copy{' '*11}(Ctrl+C)", command=copy)
edit.add_command(label=f"Paste{' '*10}(Ctrl+V)", command=paste)
edit.add_command(label=f"Select All{' '*5}(Ctrl+A)", command=selectAll)

window_ = Menu(menubar, tearoff = 0, font=("Cooper", 11))
menubar.add_cascade(label="Window", menu=window_)
window_.add_command(label=f"*Compiler {VERSION_TEXT}*", command=None)

help_ = Menu(menubar, tearoff = 0, font=("Cooper", 11))
menubar.add_cascade(label='Help', menu=help_)
help_.add_command(label='Source Code', command=lambda *_: webbrowser.open("https://github.com/MrHydroCoder/Python-Compiler", new=1))
help_.add_separator()
help_.add_command(label='Developer', command=lambda *_: webbrowser.open("https://github.com/MrHydroCoder", new=1))

root.config(menu=menubar)

Label(root, text="Made with 💝 by @MrHydroCoder", font=("Cooper Black", 25)).pack(side=BOTTOM)
root.mainloop()