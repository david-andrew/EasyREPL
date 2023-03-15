import readline

class REPL:
    """
    simple python class for creating custom REPLs. 
    manages receiving input, cursor position, and history, while the library user 

    usage:

    for line in REPL():
        <do something with line>
    """

    def __init__(self, *, prompt='>>> ', history_file=None, dedup_history=True, ctrl_c_quit=False):
        self.prompt = prompt
        self.history_file = history_file
        self.dedup_history = dedup_history
        self.ctrl_c_quit = ctrl_c_quit

        if self.history_file is not None:
            # ensure that the file exists, then pass it to readline
            with open(self.history_file, 'a'): ...
            readline.read_history_file(self.history_file)

        readline.set_auto_history(False)
      
    def __iter__(self):
        while True:
            try:
                line = input(self.prompt)

                if line.startswith('"""') or line.startswith("'''"):
                    # If the first line starts with a triple quote, continue to read input
                    # until the closing triple quote is encountered
                    delimiter, line = line[0:3], line[3:]
                    
                    lines = []
                    while True:
                        lines.append(line)
                        if line.endswith(delimiter):
                            break
                        line = input('... ')

                    # join the lines together, removing the trailing triple quote
                    line = '\n'.join(lines)
                    line = line[:-3]

                    # remove up to one newline from the beginning and end of the line
                    if line[0] == '\n':
                        line = line[1:]
                    if line[-1] == '\n':
                        line = line[:-1]

                if line:
                    if self.dedup_history:
                        #append without duplicates
                        i = 0
                        while i < readline.get_current_history_length():
                            if readline.get_history_item(i+1) == line:
                                readline.remove_history_item(i)
                            else:
                                i += 1

                    #append to history
                    readline.add_history(line)

                    #return line as next item in iteration
                    yield line

            except KeyboardInterrupt as e:
                if self.ctrl_c_quit:
                    raise e from None
                print()
                print(KeyboardInterrupt.__name__)

            except EOFError:
                break

        #save history at the end of the REPL
        if self.history_file is not None:
            readline.write_history_file(self.history_file)


def readl(*, prompt='', ctrl_c_quit=True, **kwargs):
    """read a single line using the REPL"""
    return next(iter(REPL(prompt=prompt, ctrl_c_quit=ctrl_c_quit, **kwargs)))



if __name__ == '__main__':
    #simple echo REPL
    for line in REPL(history_file='history.txt'):
        print(line)