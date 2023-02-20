from __future__ import annotations

import sys
import termios

#TODO: better handling of arrow keys
#      - single function for all arrow keys (readl interface would probably still take up/down/left/right callbacks))
#           - would use enums to select which version of the function to do
#      - callbacks can return the new line as well as the new cursor position 
#TODO: clean up the code organization

def get_cursor_pos() -> tuple[int, int]:
    """measure the current horizontal and vertical position of the cursor"""

    print('\033[6n', end='', flush=True)
    c = sys.stdin.read(1)
    assert c == '\x1b'
    c = sys.stdin.read(1)
    assert c == '['
    xpos = ''
    ypos = ''
    while True:
        c = sys.stdin.read(1)
        if c == ';':
            break
        ypos += c
    while True:
        c = sys.stdin.read(1)
        if c == 'R':
            break
        xpos += c
    xpos = int(xpos) #horizontal position
    ypos = int(ypos) #vertical position

    return xpos, ypos

def readl(up_callback=None, down_callback=None):
    """
    simple terminal line editor
    can type in text, move cursor, delete characters, and enter text
    up/down/left/right arrow keys run callback functions

    usage:

    ```
    line = readl()
    print(f'hello {line}')
    ```

    readl supports callbacks for up and down arrow keys:

    ```
    line = readl(
        up_callback=lambda line: <do something with line>,
        down_callback=lambda line: <do something with line>
    )
    ```
    up_callback and down_callback should be functions that take the current line as input and return a new line.
    E.g. if you want to implement a history, you would return the previous or next line in the history.
    """

    try:
        #turn off echo and canonical mode
        old_settings = termios.tcgetattr(sys.stdin)
        new_settings = termios.tcgetattr(sys.stdin)
        new_settings[3] = new_settings[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)
        
        # get cursor position
        xpos, ypos = get_cursor_pos()

        line = ''
        pos = 0

        def replace_line(new_line:str|None):
            nonlocal line, pos
            if new_line is not None:
                line = new_line
                pos = len(line)
                #clear text to the right of the cursor
                print(f'\033[{pos + xpos}G', end='', flush=True)
                print(f'\033[0K', end='', flush=True)

        while True:
            #display the current line
            print(f'\033[{ypos};{xpos}H', end='', flush=True)
            print(line, end='', flush=True)
            print(f'\033[{pos + xpos}G', end='', flush=True)


            c = sys.stdin.read(1)
            if c == '\x1b':
                #escape sequence
                c = sys.stdin.read(2)
                
                if c == '[A':
                    # up arrow
                    if up_callback is not None:
                        new_line = up_callback(line)
                        replace_line(new_line)

                elif c == '[B':
                    # down arrow
                    if down_callback is not None:
                        new_line = down_callback(line)
                        replace_line(new_line)
                        
                elif c == '[C':
                    # right arrow
                    if pos < len(line):
                        pos += 1
                        print(f'\033[{pos + xpos}G', end='', flush=True)
                    
                elif c == '[D':
                    #left arrow
                    if pos > 0:
                        pos -= 1
                        print(f'\033[{pos + xpos}G', end='', flush=True)
            
            elif c == '\x7f':
                #backspace
                if pos > 0:
                    line = line[:pos - 1] + line[pos:]
                    pos -= 1
                    print(f'\033[1D', end='', flush=True)  # move cursor left one position
                    print(f'\033[1P', end='', flush=True)  # delete character to the left

            elif c == '\r' or c == '\n':
                #enter
                print()
                return line
            
            elif c == '\x04':
                #ctrl-d
                print()
                raise EOFError
            
            else:
                #normal character
                line = line[:pos] + c + line[pos:]
                pos += 1
                print(f'\033[1@', end='', flush=True)
                print(c, end='', flush=True)


    finally:
        #restore old settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == '__main__':
    line = readl()
    print(f'hello {line}')