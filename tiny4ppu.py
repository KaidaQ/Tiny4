def get_pixel(VRAM, x, y):
    index = y * 16 + x
    byte = index >> 3
    bit = index & 0b111
    return (VRAM[byte] >> bit) & 1

def set_pixel(VRAM, x, y, val):
    index = y * 16 + x
    byte = index >> 3
    bit = index & 0b111
    if val:
        VRAM[byte] |= (1 << bit)
    else:
        VRAM[byte] &= ~(1 << bit)

def render_console(VRAM):
    print("=== Tiny-4 Screen ===")
    for y in range(16):
        row = ""
        for x in range(16):
            bit = get_pixel(VRAM,x,y)
            row += "█" if bit else "."
        print(row)