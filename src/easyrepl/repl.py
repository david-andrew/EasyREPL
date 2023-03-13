import readline

class REPL:
    """
    simple python class for creating custom REPLs. 
    manages receiving input, cursor position, and history, while the library user 

    usage:

    for line in REPL():
        <do something with line>
    """

    def __init__(self, prompt='>>> ', history_file=None, dedup_history=True):
        self.prompt = prompt
        self.history_file = history_file
        self.dedup_history = dedup_history

        if self.history_file is not None:
            # ensure that the file exists, then pass it to readline
            with open(self.history_file, 'a'): ...
            readline.read_history_file(self.history_file)

        readline.set_auto_history(False)
      
    def __iter__(self):
        while True:
            try:
                line = input(self.prompt)

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

            except KeyboardInterrupt:
                print()
                print(KeyboardInterrupt.__name__)

            except EOFError:
                break

        #save history at the end of the REPL
        if self.history_file is not None:
            readline.write_history_file(self.history_file)


if __name__ == '__main__':
    #simple echo REPL
    for line in REPL(history_file='history.txt'):
        print(line)