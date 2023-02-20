from line import readl

import pdb

class REPL:
    """
    simple python class for creating custom REPLs. 
    manages receiving input, cursor position, and history, while the library user 

    usage:

    for line in REPL():
        <do something with line>
    """

    def __init__(self, prompt='>>> ', history_file=None):
        self.prompt = prompt
        self.history_file = history_file

        if self.history_file is not None:
            try:
                with open(self.history_file, 'r') as f:
                    self.history = f.read().splitlines()
            except FileNotFoundError:
                self.history = []
        else:
            self.history = []
        self.index = len(self.history)

    def up_callback(self):
        if self.index > 0:
            self.index -= 1
            return self.history[self.index]
        return None
    
    def down_callback(self):
        if self.index < len(self.history)-1:
            self.index += 1
            return self.history[self.index]
        elif self.index == len(self.history)-1:
            self.index += 1
            return ''
        return None
      
    def __iter__(self):
        while True:
            try:
                print(self.prompt, end='', flush=True)
                line = readl(up_callback=lambda line: self.up_callback(),
                             down_callback=lambda line: self.down_callback())
                if line:
                    #append without duplicates
                    self.history = [h for h in self.history if h != line] + [line]
                    self.index = len(self.history)
                    yield line
            except KeyboardInterrupt:
                print()
                print(KeyboardInterrupt.__name__)
                self.index = len(self.history)
            except EOFError:
                break

        #save history at the end of the REPL
        if self.history_file is not None:
            with open(self.history_file, 'w') as f:
                f.write('\n'.join(self.history))
        

if __name__ == '__main__':
    #simple echo REPL
    for line in REPL(history_file='history.txt'):
        print(line)