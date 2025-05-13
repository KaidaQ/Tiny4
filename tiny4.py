class Tiny4CPU:
    def __init__(self):
        self.RAM = [0] * 256 # 256 bytes of memory;
        self.A = 0
        self.PC = 0
        self.running = True
        
    def load_program(self, program, start=0x00): #load ROM into RAM
        for i, byte in enumerate(program): #write bytes into the RAM
            self.RAM[start+i] = byte

    def step(self):
        opcode = self.RAM[self.PC] #current opcode will be left byte (e.g $00;0x01)
        operand = self.RAM[(self.PC + 1) & 0xFF] #current operand will be right byte (e.g $01;0x0F)
        #an opcode and operand make 1 full CPU instruction

        if opcode == 0x01: #LOAD (01:XX) // Load value from mem addr XX to reg A
            self.A = self.RAM[operand] 
            print(f"LOAD from ${opcode:02X}, value = ${self.RAM[operand]:02X}, A = ${self.A:02X}")

        elif opcode == 0x02: #STORE (02:XX) // Store value from reg A to mem addr XX
            self.RAM[operand] = self.A

        elif opcode == 0x03: #ADD (03:XX) // Add value from mem addr XX to reg A
            self.A = (self.A + self.RAM[operand]) & 0xFF

        elif opcode == 0xFF: #HALT (FF) // CPU instructions forcibly end
            self.running == False # halt the cpu instance here

        else: #invalid opcode handler
            print("Invalid opcode {opcode:02X} at {self.PC:02X}")
            self.running == False

        self.PC = (self.PC + 2) & 0xFF

    def run(self): #primitive cpu activation
        while self.running:
            self.step()