from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout

class Tiny4Debugger:
    def __init__(self,cpu):
        self.cpu = cpu
        self.console = Console()
        self.layout = Layout()

    def renderState(self):
        table = Table.grid()
        table.add_column(justify='right')
        table.add_column(justify='left')

        table.add_row("PC", f"${self.cpu.PC:02X}")
        table.add_row("A", f"${self.cpu.A:02X}")
        table.add_row("Z", str(int(self.cpu.Z)))
        table.add_row("Next", f"{self.cpu.RAM[self.cpu.PC]:02X} {self.cpu.RAM[(self.cpu.PC+1)%256]:02X}")

        return Panel(table, title="CPU State")
    # def renderMemory(self, start=0x00, end=0xFF, per_row=16):


    
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
    dbg = Tiny4Debugger(fake_cpu)

    panel = dbg.renderState()
    dbg.console.print(panel)