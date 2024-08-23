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
faces = ['( ⚆_⚆)', '(☉_☉ )'] #, '(◕‿◕ )', '( ◕‿◕)', '(⌐■_■)']
current_face_index = 0

fonts_folder = "Fonts"
font_files = [os.path.join(fonts_folder, f) for f in os.listdir(fonts_folder) if f.endswith('.ttf')]
current_font_index = 0

screen_rotation = 180

def get_char():
    """Capture a single character or escape sequence from standard input."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)
        if char == '\x1b':  # Start of an escape sequence
            next_char = sys.stdin.read(1)
            if next_char == 'O':  # F1-F4 keys start with '\x1bO'
                char += next_char + sys.stdin.read(1)
            elif next_char == '[':
                char += next_char
                next_next_char = sys.stdin.read(1)
                if next_next_char == '3':  # Detect Delete key
                    char += next_next_char + sys.stdin.read(1)  # Complete the sequence for Delete key (\x1b[3~)
                elif next_next_char == '1':  # Detect Ctrl + Arrow keys
                    char += next_next_char + sys.stdin.read(3)  # Complete the sequence for Ctrl + Arrow keys
                else:
                    char += next_next_char  # Handle other sequences like regular arrow keys
            else:
                char += next_char
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    print(f"Captured sequence: {repr(char)}")  # Debug output to confirm sequence
    return char



def wrap_text(text, font, draw, max_width):
    """Wrap text to fit within a given width, ensuring words are not split."""
    wrapped_lines = []
    lines = text.split('\n')  # Split text into lines based on newline characters

    for line in lines:
        words = line.split(' ')  # Split each line into words
        current_line = ""
        for word in words:
            if draw.textlength(current_line + word, font=font) <= max_width:
                current_line += (word + " ")
            else:
                if current_line:  # If there's already text in the line
                    wrapped_lines.append(current_line.strip())
                    current_line = word + " "
                else:  # If the word itself is too long to fit in one line
                    # Break the word itself if it's too long
                    while draw.textlength(word, font=font) > max_width:
                        # Find the maximum number of characters that fit in the width
                        for i in range(len(word)):
                            if draw.textlength(word[:i+1], font=font) > max_width:
                                break
                        wrapped_lines.append(word[:i])
                        word = word[i:]
                    current_line = word + " "
        wrapped_lines.append(current_line.strip())  # Add the last line
    return wrapped_lines


def update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height):
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)
    wrapped_lines = wrap_text(input_string, font, draw, width)  # Wrap text to fit screen width
    line_spacing = text_height + 2
    for i, line in enumerate(wrapped_lines[start_line:start_line + MAX_LINES]):
        draw.text((0, i * line_spacing), line, fill=text_color, font=font)  # Adjust line height as per your font size

    # Rotate the image if needed
    image = image.rotate(screen_rotation)

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
    start_line = 0
    cursor_position = 0
    
    while True:
        MAX_LINES = height // (text_height + 2)
        char = get_char()
        
        lines = input_string.split('\n')
        current_line = input_string[:cursor_position].count('\n')
        line_start = sum(len(line) + 1 for line in lines[:current_line])
        horizontal_position = cursor_position - line_start
        
        if current_line >= start_line + MAX_LINES:
            start_line = current_line - MAX_LINES + 1
        elif current_line < start_line:
            start_line = current_line
               
        if char == '\r':  # Enter key adds a newline
            #input_string += '\n'
            input_string = input_string[:cursor_position] + '\n' + input_string[cursor_position:]
            cursor_position += 1
            
        elif char == '\x7f':  # Backspace key
            #input_string = input_string[:-1]
            if cursor_position > 0:
                input_string = input_string[:cursor_position-1] + input_string[cursor_position:]
                cursor_position -= 1
            
        elif char == '\x1b[3~':  # Delete key
            if cursor_position < len(input_string):
                input_string = input_string[:cursor_position] + input_string[cursor_position+1:]

        elif char == '\x1bOP':  # F1 key

            if is_black_background:
                background_color = "BLACK"
                text_color = "WHITE"
                is_black_background = False
            else:
                background_color = "WHITE"
                text_color = "BLACK"
                is_black_background = True

            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height)
            continue

        elif char == '\x1bOQ':  # F2 key
            background_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height)
            continue

        elif char == '\x1bOR':  # F3 key
            text_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height)
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
            image = image.rotate(screen_rotation)

            LCD.LCD_ShowImage(image, 0, 0)
            continue
            
        elif char == '\x1b[A':  # Up Arrow key
            if current_line > 0:
                current_line -= 1
                previous_line_length = len(lines[current_line])
                cursor_position = max(line_start - previous_line_length - 1 + min(horizontal_position, previous_line_length), 0)
                if current_line < start_line:
                    start_line = current_line
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height)
            continue
        elif char == '\x1b[B':  # Down Arrow key
            if current_line < len(lines) - 1:
                current_line += 1
                next_line_length = len(lines[current_line])
                cursor_position = line_start + len(lines[current_line - 1]) + 1 + min(horizontal_position, next_line_length)
                cursor_position = min(cursor_position, len(input_string))
                if current_line >= start_line + MAX_LINES:
                    start_line = current_line - MAX_LINES + 1
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height)
            continue          
          
        elif char == '\x1b[1;5A':  # Up Arrow key
            text_height += 1
            font = ImageFont.truetype(font_files[current_font_index], text_height)
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height)
            continue

        elif char == '\x1b[1;5B':  # Down Arrow key
            if text_height >= 1:
                text_height -= 1
                font = ImageFont.truetype(font_files[current_font_index], text_height)
                update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height)
                continue
            else:
                pass  
              
        elif char == '\x1b[D':  # Left Arrow key
            if cursor_position > 0:
                cursor_position -= 1
            continue
        elif char == '\x1b[C':  # Right Arrow key
            if cursor_position < len(input_string):
                cursor_position += 1
            continue
            
        elif char == '\x1b[1;5D':  # Left Arrow key
            current_font_index = (current_font_index - 1) % len(font_files)
            font = ImageFont.truetype(font_files[current_font_index], text_height)
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height)
            continue
            
        elif char == '\x1b[1;5C':  # Right Arrow key
            current_font_index = (current_font_index + 1) % len(font_files)
            font = ImageFont.truetype(font_files[current_font_index], text_height)
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height)
            continue
            
        elif char == '\x05':  # Ctrl+E Delete all
            input_string = ""  # Clear the input string
            cursor_position = 0
            start_line = 0
            update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height)
            continue
            
        elif char == '\x03':  # Ctrl+C to exit
            break

        else:
            input_string = input_string[:cursor_position] + char + input_string[cursor_position:]
            cursor_position += 1
            
        # Adjust start_line after every input
        current_line = input_string[:cursor_position].count('\n')
        if current_line >= start_line + MAX_LINES:
            start_line = current_line - MAX_LINES + 1
        elif current_line < start_line:
            start_line = current_line
            
        # Redraw the text with the current settings
        update_BG_n_text(LCD, width, height, font, input_string, background_color, text_color, start_line, MAX_LINES, text_height)

if __name__ == '__main__':
    main()
