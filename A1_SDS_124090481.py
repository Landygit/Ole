import re

content = ""  # content string that stores the text being edited
cursor_pos = 0  # current cursor position 
undo_stack = []  # stack to store previous states 
command_history = []  # history of commands executed
last_command = None  # stores the last command 
prev_command = None  # stores the previous command
show_cursor = False  # flag to show cursor 

# function to display help information 
def print_help():
    help_text = """? - display this help info
. - toggle row cursor on and off
h - move cursor left
l - move cursor right
^ - move cursor to beginning of the line
$ - move cursor to end of the line
w - move cursor to beginning of next word
b - move cursor to beginning of previous word
i - insert <text> before cursor
a - append <text> after cursor
x - delete character at cursor
dw - delete word and trailing spaces at cursor
u - undo previous command
r - repeat last command
s - show content
q - quit program"""
    print(help_text)

# function to find the starting position of the next word 
# returns the position of the next word
# or the current position, if at the end
def find_next_word_start(s, pos):
    n = len(s)
    if pos >= n:
        return pos
    i = pos
    # skip current word
    while i < n and s[i] != ' ':
        i += 1
    # skip spaces
    while i < n and s[i] == ' ':
        i += 1
    return i

# function to find the starting position of the previous word
# return the position of the previous word or 0 if at the beginning
def find_prev_word_start(s, pos):
    if pos <= 0:
        return 0
    i = pos - 1
    # skip spaces backwards
    while i >= 0 and s[i] == ' ':
        i -= 1
    if i < 0:
        return 0
    # find the beginning of the current word
    while i > 0 and not s[i - 1].isspace():
        i -= 1
    return i

# function to display the content 
def display_content():
    global content, cursor_pos, show_cursor
    if not content:
        if show_cursor:
            print("\033[30;42m \033[0m")
        else:
            print()
        return
    if cursor_pos > len(content):
        cursor_pos = len(content)
    if not show_cursor:
        print(content)
    else:
        if cursor_pos == len(content):
            print(content + "\033[30;42m \033[0m")
        else:
            left = content[:cursor_pos]
            current = content[cursor_pos]
            right = content[cursor_pos + 1:]
            print(left + "\033[30;42m" + current + "\033[0m" + right)

# function to parse and execute the given command
# return a tuple (valid, should_display)  to indicate if the command was valid
# and if the content should be displayed after execution
def parse_and_execute(cmd):
    global content, cursor_pos, undo_stack, command_history, last_command, prev_command, show_cursor
    valid = False
    should_display = True  

    # save current state for undo if command is not ?, u, s, or q
    if cmd not in ('?', 'u', 's', 'q'):
        undo_stack.append((content, cursor_pos, show_cursor))

    # add command to history if not undo or repeat
    if cmd not in ('u', 'r'):
        command_history.append(cmd)

    # display help information
    if cmd == '?':
        print_help()
        valid = False
        should_display = False 
    # exit the program
    elif cmd == 'q':
        exit()
    # move cursor left if not at the beginning
    elif cmd == 'h':
        if cursor_pos > 0:
            cursor_pos -= 1
            valid = True
    # move cursor right if not at the end
    elif cmd == 'l':
        if cursor_pos < len(content):
            cursor_pos += 1
            valid = True
    # move cursor to the beginning of the next word
    elif cmd == 'w':
        new_pos = find_next_word_start(content, cursor_pos)
        if new_pos != cursor_pos:
            cursor_pos = new_pos
            valid = True
    # move cursor to the beginning of the previous word
    elif cmd == 'b':
        new_pos = find_prev_word_start(content, cursor_pos)
        if new_pos != cursor_pos:
            cursor_pos = new_pos
            valid = True
    # move cursor to the beginning of the line
    elif cmd in ('^', '0'):
        cursor_pos = 0
        valid = True
    # move cursor to the end of the line
    elif cmd == '$':
        if content:
            cursor_pos = len(content) - 1
            valid = True
    # remove text from cursor to the beginning of next word
    elif cmd == 'dw':
        if content:
            next_word = find_next_word_start(content, cursor_pos)
            content = content[:cursor_pos] + content[next_word:]
            valid = True
    # delete character at cursor position
    elif cmd == 'x':
        if cursor_pos < len(content):
            content = content[:cursor_pos] + content[cursor_pos + 1:]
            valid = True
    # restore previous state from undo stack
    elif cmd == 'u':
        if undo_stack:
            prev_content, prev_cursor, prev_show_cursor = undo_stack.pop()
            content = prev_content
            cursor_pos = prev_cursor
            show_cursor = prev_show_cursor
            if command_history:
                command_history.pop()
            if len(command_history) >= 1:
                prev_command = command_history[-1]
            else:
                prev_command = None
            if cursor_pos > len(content):
                cursor_pos = len(content)
            elif cursor_pos < 0:
                cursor_pos = 0
            valid = True
            if not content and not show_cursor:
                should_display = False
        else:
            should_display = False 
    # execute the previous or last command again
    elif cmd == 'r':
        if prev_command and prev_command not in ('u', '?'):
            return parse_and_execute(prev_command)
        elif last_command and last_command not in ('u', '?'):
            return parse_and_execute(last_command)
        else:
            valid = False
            should_display = False  
    # insert text before cursor position
    elif re.fullmatch(r'i.+', cmd):
        text = cmd[1:]
        content = content[:cursor_pos] + text + content[cursor_pos:]
        last_command = cmd
        valid = True
    # insert text after cursor position
    elif re.fullmatch(r'a.+', cmd):
        text = cmd[1:]
        insert_pos = cursor_pos + 1 if cursor_pos < len(content) else cursor_pos
        content = content[:insert_pos] + text + content[insert_pos:]
        cursor_pos = insert_pos + len(text) - 1
        last_command = cmd
        valid = True
    # show cursor
    elif cmd == '.':
        show_cursor = not show_cursor
        cursor_pos = 0
        valid = True
        if not content:
            should_display = False
    # show content command
    elif cmd == 's':
        valid = True

    # update last_command
    if valid and cmd not in ('u', '?'):
        if cmd != 'r':
            last_command = cmd

    return valid, should_display

# main function
def main():
    while True:
        raw_cmd = input(">")
        if raw_cmd.startswith(' '):
            continue
        cmd = raw_cmd.strip()
        result = parse_and_execute(cmd)
        valid, should_display = result
        if valid and should_display:
            display_content()

if __name__ == "__main__":
    main()
