from lib import LCD_1in44
import time
import sys
import tty
import termios
import random
import os
from PIL import Image, ImageDraw, ImageFont

# Initialize default colors as global variables
background_color = "WHITE"
text_color = "BLACK"
is_black_background = True
faces = ['( ⚆_⚆)', '(☉_☉ )', '(⌐■_■)', '(◕‿◕ )', '( ◕‿◕)']
current_face_index = 0

fonts_folder = "Fonts"
font_files = [os.path.join(fonts_folder, f) for f in os.listdir(fonts_folder) if f.endswith('.ttf')]
current_font_index = 0

def get_char():
    """Capture a single character from standard input without requiring the Enter key."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        char = sys.stdin.read(1)
        if char == '\x1b':  # Handle escape sequences (e.g., ESC, F1, or F2 key)
            next_char = sys.stdin.read(1)
            if next_char in ['O', '[']:  # Possible F1 or F2 key
                char += next_char + sys.stdin.read(1)  # Read the full escape sequence
            else:
                char = '\x1b'  # Treat as ESC if it's not an F1 or F2 sequence
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char

def wrap_text(text, font, draw, max_width):
    """Wrap text to fit within a given width, ensuring words are not split."""
    wrapped_lines = []
    lines = text.split('\n')  # Split text into lines based on newline characters

    for line in lines:
        current_line = ""
        words = line.split(' ')  # Split each line into words, keeping spaces

        for i, word in enumerate(words):
            if i == 0:
                # Handle leading spaces
                test_line = current_line + word
            else:
                test_line = current_line + " " + word  # Add space before each word except the first one

            # Measure the width of the test line
            line_width = draw.textlength(test_line, font=font)
            if line_width <= max_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line)  # Add the current line to wrapped_lines
                current_line = word  # Start a new line with the current word

        if current_line or current_line == "":  # Handle lines that are empty or have trailing spaces
            wrapped_lines.append(current_line)

    return wrapped_lines


def update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, MAX_LINES, text_height):
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)
    wrapped_lines = wrap_text(input_string, font, draw, width)  # Wrap text to fit screen width
    start_line = max(0, len(wrapped_lines) - MAX_LINES)
    line_spacing = text_height + 2
    for i, line in enumerate(wrapped_lines[start_line:]):
        draw.text((0, i * line_spacing), line, fill=text_color, font=font)  # Adjust line height as per your font size
    LCD.LCD_ShowImage(image, 0, 0)

def main():
    global background_color, text_color, is_black_background, current_font_index  # Ensure we're using the global variables

    LCD = LCD_1in44.LCD()

    Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
    LCD.LCD_Init(Lcd_ScanDir)
    LCD.LCD_Clear()

    width = LCD.width
    height = LCD.height
    text_height = 14
    font = ImageFont.truetype(font_files[current_font_index], text_height)
    font2 = ImageFont.truetype('/Fonts/DejaVuSans-Bold.ttf', 24)
    input_string = ""

    while True:
        MAX_LINES = height // (text_height + 2)
        char = get_char()
        if char == '\r':  # Enter key adds a newline
            input_string += '\n'
            
        elif char == '\x7f':  # Backspace key
            input_string = input_string[:-1]

        elif char == '\x1bOP':  # F1 key

            if is_black_background:
                background_color = "BLACK"
                text_color = "WHITE"
                is_black_background = False
            else:
                background_color = "WHITE"
                text_color = "BLACK"
                is_black_background = True

            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, MAX_LINES, text_height)
            continue

        elif char == '\x1bOQ':  # F2 key
            background_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, MAX_LINES, text_height)
            continue

        elif char == '\x1bOR':  # F3 key
            text_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, MAX_LINES, text_height)
            continue

        elif char == '\x1bOS':  # F4 key
            global current_face_index
            current_face_index = (current_face_index + 1) % len(faces)
            face = faces[current_face_index]
            image = Image.new("RGB", (width, height), background_color)
            draw = ImageDraw.Draw(image)
            text_bbox = draw.textbbox((0, 0), face, font=font2)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            position = ((width - text_width) // 2.5, (height - text_height) // 2.5)
            draw.text(position, face, fill=text_color, font=font2)

            LCD.LCD_ShowImage(image, 0, 0)
            continue
            
        elif char == '\x1b[A':  # Up Arrow key
            text_height += 1
            font = ImageFont.truetype(font_files[current_font_index], text_height)
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, MAX_LINES, text_height)
            continue

        elif char == '\x1b[B':  # Down Arrow key
            if text_height >= 1:
                text_height -= 1
                font = ImageFont.truetype(font_files[current_font_index], text_height)
                update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, MAX_LINES, text_height)
                continue
            else:
                pass  
        elif char == '\x1b[D':  # Left Arrow key
            current_font_index = (current_font_index - 1) % len(font_files)
            font = ImageFont.truetype(font_files[current_font_index], text_height)
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, MAX_LINES, text_height)
            continue
            
        elif char == '\x1b[C':  # Right Arrow key
            current_font_index = (current_font_index + 1) % len(font_files)
            font = ImageFont.truetype(font_files[current_font_index], text_height)
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, MAX_LINES, text_height)
            continue
            
        elif char == '\x1b':  # ESC key to exit
            break

        else:
            input_string += char
            
        # Redraw the text with the current settings
        update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, MAX_LINES, text_height)

if __name__ == '__main__':
    main()
