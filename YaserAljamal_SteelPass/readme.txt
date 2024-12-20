
[Project Name]

SteelPass. The name is derived from Andrew Carnegie's transformative role in the American steel industry.

[Project Description]

A password manager application that uses the CMU Graphics library. It provides a simple User Interface to the user to enter their login credentials, and it also gives the user the option to generate complex passwords. It then stores the entries encrypted in a database to keep the user’s credentials secure. It also has a built-in 2FA feature that adds extra security to the user's accounts.

[How to Run]

Run the file 'main.py' using a python3 interpreter in an environment where all the libraries listed below are installed. The app uses button icons stored in 'assets' plus a words file 'lotsofwords.txt'. On the first run, the app will immediately create 'entries.db', which is the database in which the credentials will be stored. If you (1) close the app without adding entries or (2) delete all existing entries after you created them, the app will regard the user as a new user. That is, it will let the user create a new master key, instead of asking for an initiated one and validating it, every time the user runs the app when there are no entries in 'entries.db' (even if the file and tables exist).

[Libraries]

The app uses the following non-built-in libraries:

cmu-graphics
pycryptodome
pyperclip

All of them can be installed using pip by running:

pip install cmu-graphics
pip install pycryptodome
pip install pyperclip

[Shortcut Commands]

Left mouse: PRESS on Buttons to fire the action or on Textboxes to move the focus to a new Textbox or move the cursor within a Textbox

Backspace: PRESS to remove one character and HOLD to repeat remove.

Left/Right Arrows (in Textboxes): PRESS to move the cursor by 1 character to the left/right and HOLD to repeat move.

Left/Right Arrows (in EntryViews): PRESS to navigate to the previous/next entry (wrap-around, in an alphabetical order).

Ctrl-C/Ctrl-V: PRESS to copy text from the focused Textbox / paste text to the focused Textbox.

Enter (in UnlockForm): Initiate a new master key if there are no entries or unlock the database if there are.

Shift-Tab/Tab: PRESS to move the focus to the previous Textbox / next Textbox
