import tkinter as tk
from gui import BlackjackGUI


def main():
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()