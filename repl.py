from line import readl


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

        if history_file is not None:
            with open(history_file, 'r') as f:
                self.history = f.readlines()
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
                    self.history.append(line)
                    self.index = len(self.history)
                yield line
            except KeyboardInterrupt:
                print()
                print(KeyboardInterrupt.__name__)
            except EOFError:
                break
        

if __name__ == '__main__':
    #simple echo REPL
    for line in REPL():
        print(line)