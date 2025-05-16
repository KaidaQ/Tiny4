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
    padding = data[7]
    program = data[8:8 + size]

    if padding != 0:
        print(f"Warning: Padding byte is {padding:02X} - possibly a pirated/corrupt ROM!")

    print(f"T4C v{version} Start: ${start_addr:02X} Entry: ${entry_point:02X} Size: {size} bytes!")

    pc = 0
    while pc < len(program):
        opcode = program[pc]
        operand = program[pc+1] if (pc+1) < len(program) else 0x00 # Simulate the actual Program Counter :D
        
        # LOAD AND STORE
        if opcode == 0x01:
            print(f"{pc:02X}: LOAD ${operand:02X}")
        elif opcode == 0x02:
            print(f"{pc:02X}: STORE ${operand:02X}")

        # ARITHMETIC
        elif opcode == 0x03:
            print(f"{pc:02X}: ADD ${operand:02X}")
        elif opcode == 0x04:
            print(f"{pc:02X}: SUB ${operand:02X}")
        elif opcode == 0x05:
            print(f"{pc:02X}: CMP ${operand:02X}")

        # CONTROL FLOW
        elif opcode == 0x08:
            print(f"{pc:02X}: JMP ${operand:02X}")
        elif opcode == 0x09:  
            print(f"{pc:02X}: JZ ${operand:02X}")
        elif opcode == 0x0A:
            print(f"{pc:02X}: JNZ ${operand:02X}")
        elif opcode == 0x0B:
            print(f"{pc:02X}: CALL ${operand:02X}")  
        elif opcode == 0x0C:
            print(f"{pc:02X}: RET ${operand:02X}")
        elif opcode == 0x0D:
            print(f"{pc:02X}: OUT ${operand:02X}")  

        # END LOGIC
        elif opcode == 0xFF:
            print(f"{pc:02X}: HALT")
        elif opcode == 0x00:
            print(f"{pc:02X}: NOP")

        else:
            print(f"{pc:02X}: Invalid opcode (0x{opcode:02X}) at (${pc:02X}), or data.")
        pc += 2

if __name__ == "__main__":
    file_path = input("Enter the name to your .t4c file: ").strip()
    try:
        disassemble(file_path)
    except FileNotFoundError:
        print(f"Err: File '{file_path}' not found.")
    except ValueError as e:
        print(f"Err: {e}")
