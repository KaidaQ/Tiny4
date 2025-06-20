import time
from tiny4ppu import render_console, set_pixel, get_pixel

class Tiny4CPU:
    def __init__(self):
        self.RAM = [0] * 256 # 256 bytes of memory;
        self.VRAM = [0] * 32 # 256 bits of VRAM 16x16
        self.A = 0
        self.Z = 0
        self.PC = 0

        self.vBlank = True
        self.cycles = 0

        self.running = True
        self.lastLog = ""
        self.SP = 0x5F # Stack starts below 0x60

    def set_A(self,value):
        self.A = value & 0xFF
        self.Z = (self.A == 0)

    def load_t4c(self, filepath):
        with open(filepath, "rb") as f:
            data = list(f.read())
        
        if data[0:3] != [0x54,0x34,0x43]: # Magic bytes for the header "T4C"
            raise ValueError("Invalid/malformed .t4c file!")
        
        version = data[3]
        start_addr = data[4]
        entry_point = data[5]
        size = data[6]
        padding = data[7]

        if padding != 0x00:
            print(f"Warning: Padding byte is {padding:02X} - possibly a pirated/corrupt ROM!")
        
        program = data[8:8 + size]
        self.load_program(program, start=start_addr)
        self.PC = entry_point

        print(f"Loaded Tiny-4 ROM with version v{version}! - Start: ${start_addr:02X}, Entry: ${entry_point:02X}, Size: {size} bytes!") 


    def load_program(self, program, start=0x00): #load ROM into RAM
        for i, byte in enumerate(program): #write bytes into the RAM
            self.RAM[start+i] = byte

    def step(self):
        print(f"Executing instruction PC=${self.PC:02X}")
        opcode = self.RAM[self.PC] #current opcode will be left byte (e.g $00;0x01)
        operand = self.RAM[(self.PC + 1) & 0xFF] #current operand will be right byte (e.g $01;0x0F)
        
        #an opcode and operand make 1 full CPU instruction

        # LOAD and STORE logic
        if opcode == 0x01: #LOAD (01:XX) // Load value from mem addr XX to reg A
            self.A = self.RAM[operand] 
            print(f"[LOAD] from ${opcode:02X}, value = 0x{self.RAM[operand]:02X}, A = ${self.A:02X}")

        elif opcode == 0x02: #STORE (02:XX) // Store value from reg A to mem addr XX
            if 0xE0 <= operand <= 0xFF and not self.vBlank: # Check for vblank, and writes to 0xE0 to 0xFF
                print(f"VRAM access denied outside of vBlank at PC=${self.PC:02X}")
            else:
                self.RAM[operand] = self.A
                print(f"[STORE] from ${opcode:02X}, value = 0x{self.RAM[operand]:02X}, A = ${self.A:02X}")

        # Arithmetic logic
        elif opcode == 0x03: #ADD (03:XX) // Add value from mem addr XX to reg A
            self.set_A(self.A + self.RAM[operand])
            print(f"[ADD] from ${opcode:02X}, value = 0x{self.RAM[operand]:02X}, A = ${self.A:02X}")

        elif opcode == 0x04: #SUB (04:XX) // Subtract value from mem addr XX to reg A
            self.set_A(self.A - self.RAM[operand])
            print(f"[SUB] from ${operand:02X}, value = 0x{self.RAM[operand]:02X}, A = ${self.A:02X}")

        elif opcode == 0x05: #CMP (05:XX) // Compare value from mem addr XX to reg A, set zero flag true if equal to XX
            self.Z = (self.A == self.RAM[operand])
            print(f"[CMP] A from ${self.A:02X}, RAM ${operand:02X} = ${self.RAM[operand]:02X}, Z = {int(self.Z)}")

        elif opcode == 0x06: #INC (06:XX) // Increment A register by one
            self.set_A(self.A + 1)
            print(f"[INC] from ${self.PC:02X}, A = ${self.A:02X}")
        
        elif opcode == 0x07: #DEC (07:XX) // Dncrement A register by one
            self.set_A(self.A - 1)
            print(f"[DEC] from ${self.PC:02X}, A = ${self.A:02X}")

        # Control flow
        elif opcode == 0x08: #JMP (08:XX) // Directly jump to addr XX
            self.PC = operand
            print(f"[JMP] to ${operand:02X}")
            return
        
        elif opcode == 0x09: #JZ (09:XX) // Jump if zero flag is set
            if self.Z:
                self.PC = operand
                print(f"[JZ] to ${operand:02X}")
                return
            print(f"[JZ] A is not zero. Not jumping to ${operand:02X}")

        elif opcode == 0x0A: #JNZ (0A:XX) // Jump if zero flag is NOT set
            if not self.Z:
                self.PC = operand
                print(f"[JNZ] to ${operand:02X}")
                return
            print(f"[JNZ] A is zero. Not jumping to ${operand:02X}")

        elif opcode == 0x0B: #CALL (0B:XX) // Subroutine support; Store current PC+2 val to STACK, then jump to XX
            self.RAM[self.SP] = (self.PC + 2) & 0xFF
            self.SP = (self.SP - 1) & 0xFF
            self.PC = operand
            print(f"[CALL] to ${operand:02X}")
            return
        
        elif opcode == 0x0C: #RET (0C:XX) // Subroutine support; Set PC as value in STACK
            self.SP = (self.SP + 1) & 0xFF
            self.PC = self.RAM[self.SP]
            print(f"RET to ${self.PC:02X}")
        
        elif opcode == 0x0D: #OUT (0D:XX) // Print mem contents
            print(f"[OUT] RAM[{operand:02X}] = 0x{self.RAM[operand]:02X}")

        elif opcode == 0x0E: # PUSH A // Saves current value of A reg to the STACK
            self.RAM[self.SP] = self.A
            self.SP = (self.SP - 1) & 0xFF
            print(f"[PUSH] A=0x{self.A:02X} to SP=${(self.SP + 1) & 0xFF:02X}")

        elif opcode == 0x0F: # POP A // Restores a previously saved value from the STACK to the A register
            self.SP = (self.SP + 1) & 0xFF
            self.set_A(self.RAM[self.SP])
            print(f"[POP] A=0x{self.A:02X} from SP=${self.SP:02X}")

        # End logic
        elif opcode == 0xFF: #HALT (FF) // CPU instructions forcibly end
            self.running = False # halt the cpu instance here
            print(f"[HALT] from ${self.RAM[opcode]:02X}")
            return

        elif opcode == 0x00: #NOP (00) // CPU does not do any instructions
            # Technically, the cpu physically would run this as an instruction
            # But nothing happens here...
            # Neat
            print(f"[NOP] from ${opcode:02X}")

        else: #invalid opcode handler
            print(f"Invalid opcode {opcode:02X} at {self.PC:02X}")
            self.running = False
            return
        print(f"vBlank: {self.vBlank}")

        self.cycles += 1

        # every 64 cycles, enter vertical blank for 8 cycles
        if self.cycles % 64 < 8:
            self.vBlank = True
        else:
            self.vBlank = False

        self.PC = (self.PC + 2) & 0xFF
        

    def run(self, delay): #primitive cpu activation
        while self.running:
            self.step()
            time.sleep(delay)
    
    def dump_memory(self, start=0x00, end=0xFF, bytes_per_row=16):
        print("==== Tiny-4 RAM Dump ====")
        for addr in range(start,end + 1, bytes_per_row):
            row = self.RAM[addr:addr + bytes_per_row]
            hex_bytes = ' '.join(f"{byte:02X}" for byte in row)
            print(f"{addr:02X}: {hex_bytes}")

if __name__ == "__main__":
    from tiny4ppu import render_console
    cpu = Tiny4CPU()
    filepath = input("Enter path to .t4c file: ").strip()
    delay = float(input("How fast is the cpu running per step (in seconds)"))

    try:
        cpu.load_t4c(filepath)
        cpu.run(delay)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
    except ValueError as e:
        print(f"Error: {e}")
    
    print("CPU has stopped running.")

    cpu.VRAM = cpu.RAM[0xE0:0x100] # copy VRAM from RAM
    render_console(cpu.VRAM) # display the framebuffer

    print(f"A Register: {cpu.A}")
    print()
    cpu.dump_memory()