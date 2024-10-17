import readline
from pathlib import Path


class REPL:
    """
    simple python class for creating custom REPLs. 
    manages receiving input, cursor position, and history, while the library user 

    usage:

    for line in REPL():
        <do something with line>
    """

    def __init__(self, *, prompt:str='>>> ', history_file:str|Path|None=None, dedup_history:bool=True, ctrl_c_quit:bool=False):
        self.prompt = prompt
        self.history_file = history_file
        self.external_history = '/tmp/easyrepl_external_history.txt'
        self.dedup_history = dedup_history
        self.ctrl_c_quit = ctrl_c_quit

        # ensure that the external history file exists
        Path(self.external_history).touch()

        # If set, ensure that the regular history directory and file exists, then pass it to readline
        if self.history_file is not None:
            self.history_file = Path(self.history_file).expanduser().resolve()
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self.history_file.touch()
            readline.read_history_file(self.history_file)

        # let easyrepl manually manage history
        readline.set_auto_history(False)

    def stash_history(self):
        """
        stash the current history and restore the external history
        This should be called when the line is yielded to the user
        It ensures that easyrepl's internal history doesn't interfere
        with any other processes that might use readline, e.g. pdb
        """
        readline.write_history_file(self.history_file)
        readline.clear_history()
        readline.set_auto_history(True)
        readline.read_history_file(self.external_history)

    def restore_history(self):
        """
        stash the external history and restore the current history
        This should be called after control comes back from the yielded line
        """
        readline.write_history_file(self.external_history)
        readline.set_auto_history(False)
        readline.clear_history()
        readline.read_history_file(self.history_file)

    def __del__(self):
        # clear the external history file (in-case the os doesn't in between runs)
        Path(self.external_history).unlink()

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
                        # append without duplicates
                        i = 0
                        while i < readline.get_current_history_length():
                            if readline.get_history_item(i+1) == line:
                                readline.remove_history_item(i)
                            else:
                                i += 1

                    # append to history
                    readline.add_history(line)

                    # yield line as next item in iteration, allowing the user to process it
                    # stash this history and restore any external history, in case pdb/etc. is used, they won't overlap
                    self.stash_history()
                    yield line
                    self.restore_history()

            except KeyboardInterrupt as e:
                if self.ctrl_c_quit:
                    raise e from None
                print()
                print(KeyboardInterrupt.__name__)

            except EOFError:
                break

        # save history at the end of the REPL
        if self.history_file is not None:
            readline.write_history_file(self.history_file)


def readl(*, prompt='', ctrl_c_quit=True, **kwargs):
    """read a single line using the REPL"""
    return next(iter(REPL(prompt=prompt, ctrl_c_quit=ctrl_c_quit, **kwargs)))


if __name__ == '__main__':
    # simple echo REPL
    for line in REPL(history_file='history.txt'):
        print(line)
