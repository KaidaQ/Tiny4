def disassemble(file_path):
    with open(file_path, "rb") as f:
        data = list(f.read())

    #check header
    magic = data[0:3]
    if magic != [0x54,0x34,0x43]: # Tiny-4 compiled files always have T4C in their header.
        raise ValueError("not a valid t4c file :(")
    
    version = data[3]
    start_addr = data[4]
    entry_point = data[5]
    size = data[6]
    program = data[7:7 + size]

    print(f"T4C v{version} Start: ${start_addr:02X} Entry: ${entry_point:02X} Size: {size} bytes!")

    pc = 0
    while pc < len(program):
        opcode = program[pc]
        operand = program[pc+1] if (pc+1) < len(program) else 0x00 # Simulate the actual Program Counter :D
        
        if opcode == 0x01:
            print(f"{pc:02X}: LOAD  ${operand:02X}")
        elif opcode == 0x02:
            print(f"{pc:02X}: STORE  ${operand:02X}")
        elif opcode == 0x03:
            print(f"{pc:02X}: ADD  ${operand:02X}")
        elif opcode == 0xFF:
            print(f"{pc:02X}: HALT")
        elif opcode == 0x00:
            print(f"{pc:02X}: NOP")
        else:
            print(f"{pc:02X}: Invalid opcode at ($(opcode:02X))")
        pc += 2

if __name__ == "__main__":
    disassemble("output.t4c")
