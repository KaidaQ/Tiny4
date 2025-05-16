# Tiny4
Hypothetical CPU based in Python;

A retro-like 8-bit virtual CPU designed to emulate simple bytecode instructions, akin to low level computer architecture.

Included in this project is;

- A "working" **CPU emulator** ('tiny4.py')
- A **compiler** to generate '.t4c' ROMs ('tiny4compiler.py')
- A **disassembler** for readable output ('tiny4disassembler.py')

(technically the CPU emulator is a disassembler but we dont talk about that shh)

---

## File Format 'Tiny-4 Compiled'

Tiny-4 uses a binary format with the following layout

|Offset|Size|Description|
|------|----|-----------|
|0x00  |3 Bytes |Magic Bytes|
|0x03  |1 Bytes |Version Number|
|0x04  |1 Bytes |Start addr in RAM|
|0x05  |1 Bytes |Entry point for PC|
|0x06  |1 Bytes |Program size (in bytes)|
|0x07  |1 Bytes |Region/Padding byte|
|0x08  |n Bytes |Program instruction data|

---

## CPU 'tiny4.py'

A simple fetch-decode-execute loop with:

- 256 bytes of RAM (woah!!)
- 8-bit Accumulator register (no way!!!)
- 8-bit Program Counter (real!!!)
- Simple execution methods, with 'step()' and 'run()' (super cool!!!)

## Opcode List

|Opcode|Mnemonic|Description                               |
|--------|----------|-------------------------------------------|
|0x01|`LOAD`|Load value from RAM into register `A`     |
|0x02|`STORE`|Store value from `A` into RAM             |
|0x03|`ADD`|Add value from RAM to `A`                 |
|0xFF|`HALT`|Stop execution                            |
|0x00|`NOP`|No operation                              |

and more viewable, at the CPU's website; [Tiny-4](https://kaidaq.github.io/tiny4)

---

## Compiler 'tiny4compiler.py'

This script converts a bin file into a valid Tiny-4 Compiled file:

- Sets up the Magic header
- Populates metadata (ver,entry,size)
- Writes raw instruction data
- Inbuilt fallback if no file given
- its cool

### Usage

```bash
python tiny4compiler.py 
```

---

## Disassembler 'tiny4disassembler.py'

Parses and prints out the contents of a .t4c file in readable form:

- Validates the Magic header
- Displays vers,size,start addr
- Prints each CPU instruction with opcode and operand

Change the path in the script to select the file

```bash
python tiny4disassembler.py
```

## Example Output
Disassembling e.g, a .t4c file with
```
54 34
43 01
00 00
FF 00
01 50 
02 30 
03 04 
03 04 
03 04
```

```bash
T4C v1 Start: $00 Entry: $00 Size: 255 bytes!
00: LOAD  $50
02: STORE  $30
04: ADD  $04
06: ADD  $04
08: ADD  $04
0A: ADD  $04
```

