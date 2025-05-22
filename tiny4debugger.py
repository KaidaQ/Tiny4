import tkinter as tk
from tkinter import ttk

class Tiny4Debugger:
    def __init__(self,cpu):
        self.cpu = cpu
        self.root = tk.Tk()
        self.root.title("Tiny-4 Debugger")
        self.root.geometry("800x600")

        self.cpuFrame = ttk.LabelFrame(self.root, text="CPU State")
        self.cpuFrame.pack(side="left", fill="y", padx=10, pady=10)

        self.labelPC = ttk.Label(self.cpuFrame, text="")
        self.labelA = ttk.Label(self.cpuFrame, text="")
        self.labelZ = ttk.Label(self.cpuFrame, text="")
        self.labelNext = ttk.Label(self.cpuFrame, text="")

        for widget in [self.labelPC, self.labelA, self.labelZ, self.labelNext]:
            widget.pack(anchor="w")

        self.memFrame = ttk.LabelFrame(self.root, text="RAM")
        self.memFrame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.memText = tk.Text(self.memFrame, wrap="none", font=("Courier", 10))
        self.memText.pack(fill="both", expand=True)
        

        self.update()
    
    def update(self):
        self.labelPC.config(text=f"PC: ${self.cpu.PC:02X}")
        self.labelA.config(text=f"A:  ${self.cpu.A:02X}")
        self.labelZ.config(text=f"Z:  {int(self.cpu.Z)}")
        self.labelNext.config(text=f"Next: {self.cpu.RAM[self.cpu.PC]:02X} {self.cpu.RAM[(self.cpu.PC + 1) % 256]:02X}")

        self.memText.delete("1.0", tk.END)
        for addr in range(0x00, 0x100, 16):
            row = " ".join(f"{self.cpu.RAM[addr + i]:02X}" for i in range(16))
            self.memText.insert(tk.END, f"${addr:02X}: {row}\n")

        self.root.update_idletasks()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    class FakeCPU:
        def __init__(self):
            self.PC = 0x0E
            self.A = 0x13
            self.Z = False
            self.RAM = [0x00] * 256
            self.RAM[0x0E] = 0x05
            self.RAM[0x0F] = 0x41

    fake_cpu = FakeCPU()
    gui = Tiny4Debugger(fake_cpu)
    gui.run()
