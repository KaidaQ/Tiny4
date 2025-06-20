import tkinter as tk
import tkinter.simpledialog as sd
from tkinter import ttk
from tiny4 import Tiny4CPU


class Tiny4Debugger:
    def __init__(self, cpu):
        self.cpu = cpu
        self.root = tk.Tk()
        self.root.title("Tiny-4 Debugger")
        self.root.geometry("800x600")

        self.mainFrame = ttk.Frame(self.root)
        self.mainFrame.pack(fill="both", expand=True)

        #cpu panel
        self.cpuFrame = ttk.LabelFrame(self.mainFrame, text="CPU State", width=180)
        self.cpuFrame.pack(side="left", fill="y", padx=10, pady=10)

        self.labelPC = ttk.Label(self.cpuFrame, text="")
        self.labelA = ttk.Label(self.cpuFrame, text="")
        self.labelZ = ttk.Label(self.cpuFrame, text="")
        self.labelNext = ttk.Label(self.cpuFrame, text="")

        for widget in [self.labelPC, self.labelA, self.labelZ, self.labelNext]:
            widget.pack(anchor="w", padx=10, pady=2)
            widget.config(width=20)

        self.labelInstr = ttk.Label(self.cpuFrame, text="Instruction: N/A")
        self.labelInstr.pack(anchor="w", padx=10, pady=10)
        self.labelInstr.config(width=20)

        self.rightFrame = ttk.Frame(self.mainFrame)
        self.rightFrame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.memFrame = ttk.LabelFrame(self.rightFrame, text="RAM")
        self.memFrame.pack(side="top", fill="both", expand=True)

        self.memText = tk.Text(self.memFrame, wrap="none", font=("Courier", 14))
        self.memText.pack(fill="both", expand=True)
        self.memText.bind("<Button-3>", self.onRightClickMemory)
        self.memText.config(state="disabled")

        self.ctrlFrame = ttk.Frame(self.rightFrame)
        self.ctrlFrame.pack(side="bottom", fill="x", pady=10)

        self.stepButton = ttk.Button(self.ctrlFrame, text="Step", command=self.step)
        self.runButton = ttk.Button(self.ctrlFrame, text="Run", command=self.run_cpu)
        self.resetButton = ttk.Button(self.ctrlFrame, text="Reset", command=self.reset)
        self.quitButton = ttk.Button(self.ctrlFrame, text="Quit", command=self.root.quit)

        for btn in [self.stepButton, self.runButton, self.resetButton, self.quitButton]:
            btn.pack(side="left", padx=10)

        self.memText.tag_configure("pc", background="#ffd9d9")
        self.memText.tag_configure("next", background="#d9ffd9")

        self.update()
    
    def update(self):
        self.memText.config(state="normal")  # ENABLE WRITING
        self.memText.delete("1.0", tk.END)

        for row, addr in enumerate(range(0x00, 0x100, 16)):
            bytestr = []
            for col in range(16):
                byte = self.cpu.RAM[addr + col]
                hexbyte = f"{byte:02X}"
                bytestr.append(hexbyte)

            line = f"${addr:02X}: " + " ".join(bytestr) + "\n"
            self.memText.insert(tk.END, line)

            if self.cpu.PC >= addr and self.cpu.PC < addr + 16:
                pc_col = self.cpu.PC - addr
                start = f"{row + 1}.{5 + 3 * pc_col}"
                end = f"{row + 1}.{5 + 3 * pc_col + 2}"
                self.memText.tag_add("pc", start, end)

            next_pc = (self.cpu.PC + 1) % 256
            if next_pc >= addr and next_pc < addr + 16:
                col = next_pc - addr
                start = f"{row + 1}.{8 + 3 * col}"
                end = f"{row + 1}.{8 + 3 * col + 2}"
                self.memText.tag_add("next", start, end)

        self.memText.config(state="disabled")  # LOCK WRITING

        # UPDATE CPU
        self.labelPC.config(text=f"PC: ${self.cpu.PC:02X}")
        self.labelA.config(text=f"A:  0x{self.cpu.A:02X}")
        self.labelZ.config(text=f"Z:  {int(self.cpu.Z)}")
        self.labelNext.config(
            text=f"Next: {self.cpu.RAM[self.cpu.PC]:02X} {self.cpu.RAM[(self.cpu.PC + 1) % 256]:02X}"
        )

        # opcodes
        opcode = self.cpu.RAM[self.cpu.PC]
        instruction_names = {
            0x00: "NOP", 0x01: "LOAD", 0x02: "STORE", 0x03: "ADD",
            0x04: "SUB", 0x05: "CMP", 0x06: "INC", 0x07: "DEC",
            0x08: "JMP", 0x09: "JZ", 0x0A: "JNZ", 0x0B: "CALL",
            0x0C: "RET", 0x0D: "OUT", 0x0E: "POP", 0x0F: "PUSH",
            0xFF: "HALT",
        }
        mnemonic = instruction_names.get(opcode, f"Unknown (${opcode:02X})")
        self.labelInstr.config(text=f"Instruction: {mnemonic}")

    def run(self):
        self.root.mainloop()
    
    def step(self):
            self.cpu.step()
            self.update()

    def run_cpu(self):
        import time
        while self.cpu.running:
            self.cpu.step()
            self.update()
            self.root.update()
            time.sleep(0.25)

    def reset(self):
        self.cpu = Tiny4CPU()
        self.cpu.load_t4c("output.t4c")
        self.update()

    def onRightClickMemory(self, event):
        #get mouse position
        index = self.memText.index(f"@{event.x},{event.y}")
        line, col = map(int, index.split("."))

        if line < 1 or line > 16:
            return # oob :(

        try:
            #get ram addr from line
            baseAddr = (line - 1) * 16
            relCol = (col - 6) // 3 # account for spacing and $XX
            if not (0 <= relCol < 16):
                return
            
            addr = baseAddr + relCol
            old = self.cpu.RAM[addr]

            #prompt
            result = sd.askstring("Edit Byte", f"Enter new value for ${addr:02X} (hex):", initialvalue=f"{old:02X}")
            if result is not None:
                newVal = int(result.strip(), 16) & 0xFF
                self.cpu.RAM[addr] = newVal
                self.update()
        except Exception as e:
            print("Invalid edit: ", e)

if __name__ == "__main__":
    cpu = Tiny4CPU()
    try:
        cpu.load_t4c("output.t4c")
    except Exception as e:
        print(f"Failed to load program: {e}")
        exit(1)

    gui = Tiny4Debugger(cpu)
    gui.run()

