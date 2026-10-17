
import ast
import math
import tkinter as tk
from tkinter import ttk

# ============================================================
# NEON X PRO — SCIENTIFIC CALCULATOR
# Python 3 | Tkinter | No external packages required
# ============================================================

BG = "#080D18"
PANEL = "#111827"
DISPLAY_BG = "#070B13"
BUTTON_BG = "#1B2638"
HOVER_BG = "#293B54"
CYAN = "#00E5FF"
PURPLE = "#B56BFF"
GREEN = "#39FF88"
RED = "#FF5277"
WHITE = "#F1F5F9"
MUTED = "#94A3B8"

root = tk.Tk()
root.title("NEON X PRO | Scientific Calculator")
root.geometry("1120x740")
root.minsize(850, 620)
root.configure(bg=BG)

expression = tk.StringVar()
result_text = tk.StringVar(value="READY")
mode = tk.StringVar(value="DEG")

history = []
last_answer = 0.0
just_calculated = False


# ============================================================
# SAFE MATHEMATICAL ENGINE
# ============================================================

def factorial(x):
    if x < 0 or x != int(x) or x > 170:
        raise ValueError("Factorial requires an integer from 0 to 170")
    return math.factorial(int(x))


def get_functions():
    degrees = mode.get() == "DEG"

    def trig(fn):
        def calculate(x):
            return fn(math.radians(x) if degrees else x)
        return calculate

    def inverse_trig(fn):
        def calculate(x):
            answer = fn(x)
            return math.degrees(answer) if degrees else answer
        return calculate

    return {
        "sin": trig(math.sin),
        "cos": trig(math.cos),
        "tan": trig(math.tan),
        "asin": inverse_trig(math.asin),
        "acos": inverse_trig(math.acos),
        "atan": inverse_trig(math.atan),
        "sqrt": math.sqrt,
        "log": math.log10,
        "ln": math.log,
        "abs": abs,
        "factorial": factorial,
        "exp": math.exp,
        "floor": math.floor,
        "ceil": math.ceil,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "pow": pow,
    }


def safe_evaluate(source):
    source = source.strip()

    # Convert calculator symbols into Python math syntax.
    source = source.replace("×", "*").replace("÷", "/")
    source = source.replace("−", "-").replace("π", "pi")
    source = source.replace("^", "**")

    if not source:
        raise ValueError("Enter a calculation first")

    if len(source) > 500:
        raise ValueError("Expression is too long")

    tree = ast.parse(source, mode="eval")

    functions = get_functions()
    constants = {
        "pi": math.pi,
        "e": math.e,
        "Ans": last_answer,
    }

    def evaluate(node):
        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Only numeric values are allowed")
            if abs(node.value) > 10**100:
                raise ValueError("Number is too large")
            return node.value

        if isinstance(node, ast.Name):
            if node.id in constants:
                return constants[node.id]
            raise ValueError("Unknown constant: " + node.id)

        if isinstance(node, ast.UnaryOp):
            value = evaluate(node.operand)

            if isinstance(node.op, ast.UAdd):
                return value
            if isinstance(node.op, ast.USub):
                return -value

            raise ValueError("Invalid unary operator")

        if isinstance(node, ast.BinOp):
            a = evaluate(node.left)
            b = evaluate(node.right)

            if isinstance(node.op, ast.Add):
                return a + b
            if isinstance(node.op, ast.Sub):
                return a - b
            if isinstance(node.op, ast.Mult):
                return a * b
            if isinstance(node.op, ast.Div):
                return a / b
            if isinstance(node.op, ast.Mod):
                return a % b
            if isinstance(node.op, ast.FloorDiv):
                return a // b

            if isinstance(node.op, ast.Pow):
                if abs(b) > 1000:
                    raise ValueError("Exponent is too large")
                if abs(a) > 1e100:
                    raise ValueError("Base is too large")
                return a ** b

            raise ValueError("Unsupported mathematical operator")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Invalid function")

            name = node.func.id

            if name not in functions:
                raise ValueError("Unsupported function: " + name)

            if node.keywords:
                raise ValueError("Named arguments are not supported")

            args = [evaluate(arg) for arg in node.args]
            return functions[name](*args)

        raise ValueError("Invalid mathematical expression")

    answer = evaluate(tree.body)

    if isinstance(answer, complex):
        raise ValueError("Complex answers are not supported")

    if not math.isfinite(answer):
        raise ValueError("Result is outside the supported range")

    return answer


def format_number(number):
    if number == 0:
        return "0"

    if isinstance(number, int):
        return str(number)

    if abs(number) >= 1e12 or abs(number) < 1e-8:
        return f"{number:.8e}"

    return f"{number:.12g}"


# ============================================================
# CALCULATOR OPERATIONS
# ============================================================

def insert(value):
    global just_calculated

    current = expression.get()

    if just_calculated:
        if value in ("+", "-", "*", "/", "**", "%"):
            just_calculated = False
        else:
            current = ""
            expression.set("")
            just_calculated = False

    expression.set(current + value)
    result_text.set("READY")


def insert_function(name):
    global just_calculated

    current = expression.get().strip()

    if just_calculated:
        current = ""
        expression.set("")
        just_calculated = False

    if current:
        # Wrap the existing expression, e.g. 25 becomes sqrt(25).
        expression.set(f"{name}({current})")
    else:
        expression.set(name + "(")

    result_text.set("READY")
    entry.icursor(tk.END)
    entry.focus_set()


def apply_square():
    global just_calculated

    current = expression.get().strip()
    if current:
        expression.set(f"({current})**2")
        just_calculated = False
        result_text.set("READY")
    entry.focus_set()


def apply_factorial():
    global just_calculated

    current = expression.get().strip()

    if current:
        expression.set(f"factorial({current})")
        just_calculated = False
        result_text.set("READY")
    else:
        expression.set("factorial(")

    entry.icursor(tk.END)
    entry.focus_set()


def apply_percent():
    global just_calculated

    current = expression.get().strip()
    if current:
        expression.set(f"({current})/100")
        just_calculated = False
        result_text.set("READY")
    entry.focus_set()


def clear():
    global just_calculated

    expression.set("")
    result_text.set("READY")
    just_calculated = False
    entry.focus_set()


def backspace():
    global just_calculated

    expression.set(expression.get()[:-1])
    result_text.set("READY")
    just_calculated = False
    entry.focus_set()


def calculate(event=None):
    global last_answer, just_calculated

    source = expression.get().strip()

    if not source:
        return "break"

    try:
        answer = safe_evaluate(source)
        formatted = format_number(answer)

        last_answer = answer
        result_text.set("= " + formatted)

        history.insert(0, (source, formatted))
        del history[100:]

        history_list.delete(0, tk.END)
        for item, result in history:
            history_list.insert(tk.END, f"{item} = {result}")

        just_calculated = True

    except (ValueError, SyntaxError, TypeError,
            ArithmeticError, OverflowError, RecursionError) as error:
        result_text.set("ERROR: " + str(error))
        just_calculated = False

    return "break"


def toggle_mode():
    new_mode = "RAD" if mode.get() == "DEG" else "DEG"
    mode.set(new_mode)
    mode_button.config(text=new_mode)
    result_text.set("Angle mode: " + new_mode)
    entry.focus_set()


def load_history(event=None):
    selection = history_list.curselection()

    if selection:
        index = selection[0]
        expression.set(history[index][0])
        result_text.set("History loaded")
        global just_calculated
        just_calculated = False
        entry.focus_set()


def clear_history():
    history.clear()
    history_list.delete(0, tk.END)


# ============================================================
# VISUAL INTERFACE
# ============================================================

def make_button(parent, text, command, color=WHITE,
                background=BUTTON_BG, size=12):

    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=background,
        fg=color,
        activebackground=HOVER_BG,
        activeforeground=CYAN,
        font=("Segoe UI", size, "bold"),
        relief="flat",
        bd=0,
        cursor="hand2",
        highlightthickness=0,
        padx=4,
        pady=8,
    )

    button.bind(
        "<Enter>",
        lambda event: button.configure(bg=HOVER_BG)
    )
    button.bind(
        "<Leave>",
        lambda event: button.configure(bg=background)
    )

    return button


# Header
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=24, pady=(16, 12))

tk.Label(
    header, text="NEON",
    bg=BG, fg=CYAN,
    font=("Segoe UI", 27, "bold")
).pack(side="left")

tk.Label(
    header, text=" X PRO",
    bg=BG, fg=PURPLE,
    font=("Segoe UI", 27, "bold")
).pack(side="left")

tk.Label(
    header,
    text="SCIENTIFIC COMPUTING SYSTEM",
    bg=BG, fg=MUTED,
    font=("Consolas", 10)
).pack(side="left", padx=18, pady=(12, 0))

tk.Label(
    header,
    text="● SYSTEM ONLINE",
    bg=BG, fg=GREEN,
    font=("Consolas", 10, "bold")
).pack(side="right", pady=12)


# Main layout
main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=24, pady=(0, 18))

main.columnconfigure(0, weight=3)
main.columnconfigure(1, weight=1, minsize=230)
main.rowconfigure(0, weight=1)

calculator = tk.Frame(
    main, bg=PANEL, padx=16, pady=16
)
calculator.grid(
    row=0, column=0, sticky="nsew", padx=(0, 14)
)


# Display
display = tk.Frame(
    calculator,
    bg=DISPLAY_BG,
    padx=16,
    pady=12,
    highlightbackground="#20384A",
    highlightthickness=1
)
display.pack(fill="x", pady=(0, 14))

tk.Label(
    display,
    text="EXPRESSION",
    bg=DISPLAY_BG,
    fg=MUTED,
    font=("Consolas", 9)
).pack(anchor="w")

entry = tk.Entry(
    display,
    textvariable=expression,
    bg=DISPLAY_BG,
    fg=WHITE,
    insertbackground=CYAN,
    font=("Consolas", 22),
    relief="flat",
    bd=0,
    justify="right",
)
entry.pack(fill="x", pady=(8, 10), ipady=5)

tk.Label(
    display,
    textvariable=result_text,
    bg=DISPLAY_BG,
    fg=CYAN,
    font=("Consolas", 14, "bold"),
    anchor="e",
).pack(fill="x")


# Scientific keypad
button_frame = tk.Frame(calculator, bg=PANEL)
button_frame.pack(fill="both", expand=True)

for column in range(6):
    button_frame.columnconfigure(
        column, weight=1, uniform="columns"
    )

for row in range(7):
    button_frame.rowconfigure(
        row, weight=1, uniform="rows"
    )


# Top utility row: no overlapping buttons
mode_button = make_button(
    button_frame, "DEG", toggle_mode, CYAN
)
mode_button.grid(
    row=0, column=0, sticky="nsew", padx=3, pady=3
)

make_button(
    button_frame, "AC", clear, RED, "#321B2A"
).grid(row=0, column=1, sticky="nsew", padx=3, pady=3)

make_button(
    button_frame, "⌫", backspace, RED, "#321B2A"
).grid(row=0, column=2, sticky="nsew", padx=3, pady=3)

make_button(
    button_frame, "Ans", lambda: insert("Ans"), CYAN
).grid(row=0, column=3, sticky="nsew", padx=3, pady=3)

make_button(
    button_frame, "π", lambda: insert("pi"), PURPLE
).grid(row=0, column=4, sticky="nsew", padx=3, pady=3)

make_button(
    button_frame, "e", lambda: insert("e"), PURPLE
).grid(row=0, column=5, sticky="nsew", padx=3, pady=3)


# Button definitions: label, action, row, column, color
buttons = [
    ("sin", lambda: insert_function("sin"), 1, 0, PURPLE),
    ("cos", lambda: insert_function("cos"), 1, 1, PURPLE),
    ("tan", lambda: insert_function("tan"), 1, 2, PURPLE),
    ("asin", lambda: insert_function("asin"), 1, 3, PURPLE),
    ("acos", lambda: insert_function("acos"), 1, 4, PURPLE),
    ("atan", lambda: insert_function("atan"), 1, 5, PURPLE),

    ("√", lambda: insert_function("sqrt"), 2, 0, PURPLE),
    ("x²", apply_square, 2, 1, PURPLE),
    ("xʸ", lambda: insert("**"), 2, 2, PURPLE),
    ("log", lambda: insert_function("log"), 2, 3, PURPLE),
    ("ln", lambda: insert_function("ln"), 2, 4, PURPLE),
    ("n!", apply_factorial, 2, 5, PURPLE),

    ("7", lambda: insert("7"), 3, 0, WHITE),
    ("8", lambda: insert("8"), 3, 1, WHITE),
    ("9", lambda: insert("9"), 3, 2, WHITE),
    ("÷", lambda: insert("/"), 3, 3, CYAN),
    ("(", lambda: insert("("), 3, 4, WHITE),
    (")", lambda: insert(")"), 3, 5, WHITE),

    ("4", lambda: insert("4"), 4, 0, WHITE),
    ("5", lambda: insert("5"), 4, 1, WHITE),
    ("6", lambda: insert("6"), 4, 2, WHITE),
    ("×", lambda: insert("*"), 4, 3, CYAN),
    ("%", apply_percent, 4, 4, WHITE),
    ("abs", lambda: insert_function("abs"), 4, 5, PURPLE),

    ("1", lambda: insert("1"), 5, 0, WHITE),
    ("2", lambda: insert("2"), 5, 1, WHITE),
    ("3", lambda: insert("3"), 5, 2, WHITE),
    ("−", lambda: insert("-"), 5, 3, CYAN),
    ("floor", lambda: insert_function("floor"), 5, 4, PURPLE),
    ("ceil", lambda: insert_function("ceil"), 5, 5, PURPLE),

    ("0", lambda: insert("0"), 6, 0, WHITE),
    (".", lambda: insert("."), 6, 1, WHITE),
    ("exp", lambda: insert_function("exp"), 6, 2, PURPLE),
    ("+", lambda: insert("+"), 6, 3, CYAN),
]

for label, action, row, column, color in buttons:
    make_button(
        button_frame, label, action, color=color
    ).grid(
        row=row, column=column,
        sticky="nsew", padx=3, pady=3
    )

make_button(
    button_frame, "=", calculate, "#06111A", CYAN, 16
).grid(
    row=6, column=4, columnspan=2,
    sticky="nsew", padx=3, pady=3
)


# ============================================================
# CALCULATION HISTORY
# ============================================================

side = tk.Frame(main, bg=PANEL, padx=14, pady=16)
side.grid(row=0, column=1, sticky="nsew")

tk.Label(
    side,
    text="CALC HISTORY",
    bg=PANEL, fg=CYAN,
    font=("Segoe UI", 13, "bold")
).pack(anchor="w")

tk.Label(
    side,
    text="Your recent calculations",
    bg=PANEL, fg=MUTED,
    font=("Segoe UI", 9)
).pack(anchor="w", pady=(4, 12))

history_list = tk.Listbox(
    side,
    bg=DISPLAY_BG,
    fg=WHITE,
    selectbackground="#164E63",
    selectforeground=CYAN,
    font=("Consolas", 9),
    relief="flat",
    borderwidth=0,
    activestyle="none",
    exportselection=False,
)
history_list.pack(fill="both", expand=True)
history_list.bind("<Double-Button-1>", load_history)

make_button(
    side, "LOAD SELECTED", load_history, CYAN
).pack(fill="x", pady=(12, 5))

make_button(
    side, "CLEAR HISTORY", clear_history, RED
).pack(fill="x", pady=5)

tk.Label(
    side,
    text="QUICK TIPS\n\n"
         "Enter = Calculate\n"
         "Esc = Clear\n"
         "Use pi, e and Ans\n"
         "Double-click history\n"
         "to restore an expression.",
    bg=PANEL, fg=MUTED,
    font=("Segoe UI", 9),
    justify="left",
).pack(anchor="w", pady=(16, 0))


# Footer
footer = tk.Frame(root, bg=BG)
footer.pack(fill="x", padx=24, pady=(0, 12))

tk.Label(
    footer,
    text="NEON X PRO  •  PYTHON EDITION  •  SCIENTIFIC MODE",
    bg=BG, fg=MUTED,
    font=("Consolas", 9)
).pack(side="left")

tk.Label(
    footer,
    text="BUILT WITH PYTHON",
    bg=BG, fg=GREEN,
    font=("Consolas", 9)
).pack(side="right")


# Keyboard support
entry.bind("<Return>", calculate)
entry.bind("<KP_Enter>", calculate)
root.bind("<Escape>", lambda event: clear())

entry.focus_set()
root.mainloop()
