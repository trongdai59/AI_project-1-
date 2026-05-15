

import __main__

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import tkinter as tk
from tkinter import ttk

# ------------------ XAY DUNG HE THONG MO (27 LUAT) ------------------
load = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'load')
dirt = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'dirt')
fabric = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'fabric')
wash_time = ctrl.Consequent(np.arange(0, 120.1, 0.1), 'wash_time')
water_level = ctrl.Consequent(np.arange(0, 10.1, 0.1), 'water_level')

# Tap mo
# LOAD
load['S'] = fuzz.trimf(load.universe, [0, 0, 3])
load['M'] = fuzz.trimf(load.universe, [2, 5, 8])
load['L'] = fuzz.trimf(load.universe, [7, 10, 10])

# DIRT
dirt['L'] = fuzz.trimf(dirt.universe, [0, 0, 3])
dirt['M'] = fuzz.trimf(dirt.universe, [2, 5, 8])
dirt['H'] = fuzz.trimf(dirt.universe, [7, 10, 10])

# FABRIC
fabric['D'] = fuzz.trimf(fabric.universe, [0, 0, 3])
fabric['N'] = fuzz.trimf(fabric.universe, [2, 5, 8])
fabric['H'] = fuzz.trimf(fabric.universe, [7, 10, 10])


wash_time['S'] = fuzz.trimf(wash_time.universe, [0,0,40])
wash_time['M'] = fuzz.trimf(wash_time.universe, [30,60,90])
wash_time['L'] = fuzz.trimf(wash_time.universe, [80,120,120])

water_level['L'] = fuzz.trimf(water_level.universe, [0,0,4])
water_level['M'] = fuzz.trimf(water_level.universe, [2,5,8])
water_level['H'] = fuzz.trimf(water_level.universe, [6,10,10])

# Danh sach luat (27 luat theo dung bang)
rules = [
    ctrl.Rule(load['S'] & dirt['L'] & fabric['D'], (wash_time['S'], water_level['L'])),
    ctrl.Rule(load['S'] & dirt['L'] & fabric['N'], (wash_time['S'], water_level['L'])),
    ctrl.Rule(load['S'] & dirt['L'] & fabric['H'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['S'] & dirt['M'] & fabric['D'], (wash_time['M'], water_level['L'])),
    ctrl.Rule(load['S'] & dirt['M'] & fabric['N'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['S'] & dirt['M'] & fabric['H'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['S'] & dirt['H'] & fabric['D'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['S'] & dirt['H'] & fabric['N'], (wash_time['L'], water_level['M'])),
    ctrl.Rule(load['S'] & dirt['H'] & fabric['H'], (wash_time['L'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['L'] & fabric['D'], (wash_time['S'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['L'] & fabric['N'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['L'] & fabric['H'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['M'] & fabric['D'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['M'] & fabric['N'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['M'] & fabric['H'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['M'] & dirt['H'] & fabric['D'], (wash_time['L'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['H'] & fabric['N'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['M'] & dirt['H'] & fabric['H'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['L'] & fabric['D'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['L'] & dirt['L'] & fabric['N'], (wash_time['M'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['L'] & fabric['H'], (wash_time['M'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['M'] & fabric['D'], (wash_time['M'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['M'] & fabric['N'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['M'] & fabric['H'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['H'] & fabric['D'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['H'] & fabric['N'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['H'] & fabric['H'], (wash_time['L'], water_level['H']))
]
washing_system = ctrl.ControlSystem(rules)

# ------------------ GIAO DIEN TKINTER ------------------
class WasherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("May Giat Thong Minh")
        self.root.geometry("700x500")
        self.root.configure(bg='#2c3e50')

        # Canvas chinh
        self.canvas = tk.Canvas(root, width=680, height=480, bg='#ecf0f1', highlightthickness=0)
        self.canvas.place(x=10, y=10)

        # Vien may
        self.canvas.create_rectangle(10, 10, 670, 470, outline='#7f8c8d', fill='#bdc3c7', width=3)

        # Man hinh LCD
        self.canvas.create_rectangle(50, 40, 350, 140, fill='#2c3e50', outline='#1a252f', width=2)
        self.canvas.create_text(200, 65, text="THOI GIAN GIAT", fill='#ecf0f1', font=('Arial', 12, 'bold'))
        self.time_display = self.canvas.create_text(200, 105, text="0 phut", fill='#e67e22', font=('Arial', 20, 'bold'))

        self.canvas.create_rectangle(390, 40, 630, 140, fill='#2c3e50', outline='#1a252f', width=2)
        self.canvas.create_text(510, 65, text="MUC NUOC", fill='#ecf0f1', font=('Arial', 12, 'bold'))
        self.water_display = self.canvas.create_text(510, 105, text="0.0 (0-10)", fill='#e67e22', font=('Arial', 16, 'bold'))

        # Cac thanh truot (Scale)
        style = ttk.Style()
        style.configure("TScale", background="#bdc3c7")

        ttk.Label(self.canvas, text="Tai trong (0-10)", background="#bdc3c7", font=('Arial', 10)).place(x=60, y=180)
        self.load_var = tk.DoubleVar(value=5.0)
        self.load_scale = ttk.Scale(self.canvas, from_=0, to=10, variable=self.load_var, length=200, command=self.update)
        self.load_scale.place(x=60, y=210)
        self.load_lbl = ttk.Label(self.canvas, text="5.0", background="#bdc3c7", font=('Arial', 10))
        self.load_lbl.place(x=280, y=205)

        ttk.Label(self.canvas, text="Do ban (0-10)", background="#bdc3c7", font=('Arial', 10)).place(x=60, y=260)
        self.dirt_var = tk.DoubleVar(value=5.0)
        self.dirt_scale = ttk.Scale(self.canvas, from_=0, to=10, variable=self.dirt_var, length=200, command=self.update)
        self.dirt_scale.place(x=60, y=290)
        self.dirt_lbl = ttk.Label(self.canvas, text="5.0", background="#bdc3c7", font=('Arial', 10))
        self.dirt_lbl.place(x=280, y=285)

        ttk.Label(self.canvas, text="Loai vai (0=mem,10=cung)", background="#bdc3c7", font=('Arial', 10)).place(x=60, y=340)
        self.fabric_var = tk.DoubleVar(value=5.0)
        self.fabric_scale = ttk.Scale(self.canvas, from_=0, to=10, variable=self.fabric_var, length=200, command=self.update)
        self.fabric_scale.place(x=60, y=370)
        self.fabric_lbl = ttk.Label(self.canvas, text="5.0", background="#bdc3c7", font=('Arial', 10))
        self.fabric_lbl.place(x=280, y=365)

        # Nut START
        self.start_btn = tk.Button(self.canvas, text="BAT DAU GIAT", command=self.calculate, bg='#e67e22', fg='white', font=('Arial', 12, 'bold'))
        self.start_btn.place(x=420, y=250, width=180, height=50)

        # Trang thai
        self.status = tk.Label(self.canvas, text="San sang", bg='#bdc3c7', fg='#2c3e50', font=('Arial', 10))
        self.status.place(x=420, y=330)

        self.update()  # Hien thi ban dau

    def update(self, event=None):
        # Cap nhat gia tri hien thi khi keo thanh truot
        self.load_lbl.config(text=f"{self.load_var.get():.1f}")
        self.dirt_lbl.config(text=f"{self.dirt_var.get():.1f}")
        self.fabric_lbl.config(text=f"{self.fabric_var.get():.1f}")
        self.calculate()  # Tu dong tinh toan khi keo

    def calculate(self):
        try:
            sim = ctrl.ControlSystemSimulation(washing_system)
            sim.input['load'] = self.load_var.get()
            sim.input['dirt'] = self.dirt_var.get()
            sim.input['fabric'] = self.fabric_var.get()
            sim.compute()
            wt = sim.output['wash_time']
            wl = sim.output['water_level']
            self.canvas.itemconfig(self.time_display, text=f"{int(round(wt))} phut")
            self.canvas.itemconfig(self.water_display, text=f"{wl:.1f} (0-10)")
            self.status.config(text="Da tinh xong", fg='green')
        except Exception as e:
            self.status.config(text=f"Loi: {str(e)}", fg='red')

if __name__ == "__main__":
    root = tk.Tk()
    app = WasherApp(root)
    root.mainloop()
# Cai dat thu vien (chay 1 lan)

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import tkinter as tk
from tkinter import ttk

# ------------------ XAY DUNG HE THONG MO (27 LUAT) ------------------
load = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'load')
dirt = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'dirt')
fabric = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'fabric')
wash_time = ctrl.Consequent(np.arange(0, 120.1, 0.1), 'wash_time')
water_level = ctrl.Consequent(np.arange(0, 10.1, 0.1), 'water_level')

# Tap mo
# LOAD
load['S'] = fuzz.trimf(load.universe, [0, 0, 3])
load['M'] = fuzz.trimf(load.universe, [2, 5, 8])
load['L'] = fuzz.trimf(load.universe, [7, 10, 10])

# DIRT
dirt['L'] = fuzz.trimf(dirt.universe, [0, 0, 3])
dirt['M'] = fuzz.trimf(dirt.universe, [2, 5, 8])
dirt['H'] = fuzz.trimf(dirt.universe, [7, 10, 10])

# FABRIC
fabric['D'] = fuzz.trimf(fabric.universe, [0, 0, 3])
fabric['N'] = fuzz.trimf(fabric.universe, [2, 5, 8])
fabric['H'] = fuzz.trimf(fabric.universe, [7, 10, 10])


wash_time['S'] = fuzz.trimf(wash_time.universe, [0,0,40])
wash_time['M'] = fuzz.trimf(wash_time.universe, [30,60,90])
wash_time['L'] = fuzz.trimf(wash_time.universe, [80,120,120])

water_level['L'] = fuzz.trimf(water_level.universe, [0,0,4])
water_level['M'] = fuzz.trimf(water_level.universe, [2,5,8])
water_level['H'] = fuzz.trimf(water_level.universe, [6,10,10])

# Danh sach luat (27 luat theo dung bang)
rules = [
    ctrl.Rule(load['S'] & dirt['L'] & fabric['D'], (wash_time['S'], water_level['L'])),
    ctrl.Rule(load['S'] & dirt['L'] & fabric['N'], (wash_time['S'], water_level['L'])),
    ctrl.Rule(load['S'] & dirt['L'] & fabric['H'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['S'] & dirt['M'] & fabric['D'], (wash_time['M'], water_level['L'])),
    ctrl.Rule(load['S'] & dirt['M'] & fabric['N'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['S'] & dirt['M'] & fabric['H'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['S'] & dirt['H'] & fabric['D'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['S'] & dirt['H'] & fabric['N'], (wash_time['L'], water_level['M'])),
    ctrl.Rule(load['S'] & dirt['H'] & fabric['H'], (wash_time['L'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['L'] & fabric['D'], (wash_time['S'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['L'] & fabric['N'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['L'] & fabric['H'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['M'] & fabric['D'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['M'] & fabric['N'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['M'] & fabric['H'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['M'] & dirt['H'] & fabric['D'], (wash_time['L'], water_level['M'])),
    ctrl.Rule(load['M'] & dirt['H'] & fabric['N'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['M'] & dirt['H'] & fabric['H'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['L'] & fabric['D'], (wash_time['M'], water_level['M'])),
    ctrl.Rule(load['L'] & dirt['L'] & fabric['N'], (wash_time['M'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['L'] & fabric['H'], (wash_time['M'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['M'] & fabric['D'], (wash_time['M'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['M'] & fabric['N'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['M'] & fabric['H'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['H'] & fabric['D'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['H'] & fabric['N'], (wash_time['L'], water_level['H'])),
    ctrl.Rule(load['L'] & dirt['H'] & fabric['H'], (wash_time['L'], water_level['H']))
]
washing_system = ctrl.ControlSystem(rules)

# ------------------ GIAO DIEN TKINTER ------------------
class WasherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("May Giat Thong Minh")
        self.root.geometry("700x500")
        self.root.configure(bg='#2c3e50')

        # Canvas chinh
        self.canvas = tk.Canvas(root, width=680, height=480, bg='#ecf0f1', highlightthickness=0)
        self.canvas.place(x=10, y=10)

        # Vien may
        self.canvas.create_rectangle(10, 10, 670, 470, outline='#7f8c8d', fill='#bdc3c7', width=3)

        # Man hinh LCD
        self.canvas.create_rectangle(50, 40, 350, 140, fill='#2c3e50', outline='#1a252f', width=2)
        self.canvas.create_text(200, 65, text="THỜI GIAN GIẶT", fill='#ecf0f1', font=('Arial', 12, 'bold'))
        self.time_display = self.canvas.create_text(200, 105, text="0 phút", fill='#e67e22', font=('Arial', 20, 'bold'))

        self.canvas.create_rectangle(390, 40, 630, 140, fill='#2c3e50', outline='#1a252f', width=2)
        self.canvas.create_text(510, 65, text="MỰC NƯỚC", fill='#ecf0f1', font=('Arial', 12, 'bold'))
        self.water_display = self.canvas.create_text(510, 105, text="0.0", fill='#e67e22', font=('Arial', 16, 'bold'))

        # Cac thanh truot (Scale)
        style = ttk.Style()
        style.configure("TScale", background="#bdc3c7")

        ttk.Label(self.canvas, text="Khối lượng giặt (nhỏ, trung bình, lớn)", background="#bdc3c7", font=('Arial', 10)).place(x=60, y=180)
        self.load_var = tk.DoubleVar(value=5.0)
        self.load_scale = ttk.Scale(self.canvas, from_=0, to=10, variable=self.load_var, length=200, command=self.update)
        self.load_scale.place(x=60, y=210)
        self.load_lbl = ttk.Label(self.canvas, text="5.0", background="#bdc3c7", font=('Arial', 10))
        self.load_lbl.place(x=280, y=205)

        ttk.Label(self.canvas, text="Độ bẩn (thấp, trung bình, cao)", background="#bdc3c7", font=('Arial', 10)).place(x=60, y=260)
        self.dirt_var = tk.DoubleVar(value=5.0)
        self.dirt_scale = ttk.Scale(self.canvas, from_=0, to=10, variable=self.dirt_var, length=200, command=self.update)
        self.dirt_scale.place(x=60, y=290)
        self.dirt_lbl = ttk.Label(self.canvas, text="5.0", background="#bdc3c7", font=('Arial', 10))
        self.dirt_lbl.place(x=280, y=285)

        ttk.Label(self.canvas, text="Loại vải (mỏng, bình thường, nặng)", background="#bdc3c7", font=('Arial', 10)).place(x=60, y=340)
        self.fabric_var = tk.DoubleVar(value=5.0)
        self.fabric_scale = ttk.Scale(self.canvas, from_=0, to=10, variable=self.fabric_var, length=200, command=self.update)
        self.fabric_scale.place(x=60, y=370)
        self.fabric_lbl = ttk.Label(self.canvas, text="5.0", background="#bdc3c7", font=('Arial', 10))
        self.fabric_lbl.place(x=280, y=365)

        # Nut START
        self.start_btn = tk.Button(self.canvas, text="BẮT ĐẦU GIẶT", command=self.calculate, bg='#e67e22', fg='white', font=('Arial', 12, 'bold'))
        self.start_btn.place(x=420, y=250, width=180, height=50)

        # Trang thai
        self.status = tk.Label(self.canvas, text="SẴN SÀNG", bg='#bdc3c7', fg='#2c3e50', font=('Arial', 10))
        self.status.place(x=420, y=330)

        self.update()  # Hien thi ban dau

    def update(self, event=None):
        # Cap nhat gia tri hien thi khi keo thanh truot
        self.load_lbl.config(text=f"{self.load_var.get():.1f}")
        self.dirt_lbl.config(text=f"{self.dirt_var.get():.1f}")
        self.fabric_lbl.config(text=f"{self.fabric_var.get():.1f}")
        self.calculate()  # Tu dong tinh toan khi keo

    def calculate(self):
        try:
            sim = ctrl.ControlSystemSimulation(washing_system)
            sim.input['load'] = self.load_var.get()
            sim.input['dirt'] = self.dirt_var.get()
            sim.input['fabric'] = self.fabric_var.get()
            sim.compute()
            wt = sim.output['wash_time']
            wl = sim.output['water_level']
            self.canvas.itemconfig(self.time_display, text=f"{int(round(wt))} phut")
            self.canvas.itemconfig(self.water_display, text=f"{wl:.1f}")
            self.status.config(text="Da tinh xong", fg='green')
        except Exception as e:
            self.status.config(text=f"Loi: {str(e)}", fg='red')

if __name__ == "__main__":
    root = tk.Tk()
    app = WasherApp(root)
    root.mainloop()