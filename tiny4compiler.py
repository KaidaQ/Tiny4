import os
# tiny 4 compiler!
# this file will compile a given binary file into the .t4c file extension, so the CPU can read it!!!

# i/o configs
input_file = "input.bin"
output_file = "output.t4c"

if os.path.exists(output_file):
    os.remove(output_file)


# test program if none is given
test_program = [
    0x03, 0x02,
    0x03, 0x02,
    0x03, 0x02,
    0xFF, 0x00
] # ADD will occur 3 times, and will HALT at end of execution.

if os.path.exists(input_file):
    print(f"found bin input: {input_file}")
    with open(input_file, "rb") as f:
        program = list(f.read())
else:
    print("no file found :( resorting to default testing program")
    program = test_program

# TINY 4 COMPILED FILE FORMAT SPECS
magic = b'T4C'
version = 0x01
start_addr = 0x00
entry_point = 0x00
program_size = len(program)

# Write to .t4c output
if __name__ == "__main__":
    with open(output_file, "wb") as f:
        f.write(magic)
        f.write(bytes([version]))
        f.write(bytes([start_addr]))
        f.write(bytes([entry_point]))
        f.write(bytes([program_size]))
        f.write(bytes(program))

print(f"successfully compiled t {output_file} ({program_size} bytes!)")