# This program was made by:
#
# Nilo Martins and Ricardo Paranhos
#
# to a class of Computer Intelligence
#
# by Prof. Fernando Buarque, PhD
#
# from University of Pernambuco – UPE,
# School of Engineering – POLI
#
# Year 2018
#
# This software are licensed by GPLv3
#
# Contact: jniloms@gmail.com

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygubu
from specialistSystem import makerulesfile, maketests, analysefile

class Application:

    def __init__(self, master):

        self.master = master
        self.builder = builder = pygubu.Builder()
        builder.add_from_file('main.ui')
        self.mainwindow = builder.get_object('mainwindow', master)
        builder.connect_callbacks(self)

        self.fileC1 = tk.StringVar(master)
        edit = self.builder.get_object('Entry_fileC1')
        edit.config(textvariable=self.fileC1)

        self.c1 = tk.StringVar(master)
        edit = self.builder.get_object('Entry_nameC1')
        edit.config(textvariable=self.c1)

        self.fileC2 = tk.StringVar(master)
        edit = self.builder.get_object('Entry_fileC2')
        edit.config(textvariable=self.fileC2)

        self.c2 = tk.StringVar(master)
        edit = self.builder.get_object('Entry_nameC2')
        edit.config(textvariable=self.c2)

        self.rulesFile = tk.StringVar(master)
        edit = self.builder.get_object('Entry_rulesFile')
        edit.config(textvariable=self.rulesFile)

        edit = self.builder.get_object('Entry_rulesFile2')
        edit.config(textvariable=self.rulesFile)

        self.dataFile = tk.StringVar(master)
        edit = self.builder.get_object('Entry_dataFile')
        edit.config(textvariable=self.dataFile)

        self.resultFile = tk.StringVar(master)
        edit = self.builder.get_object('Entry_resultFile')
        edit.config(textvariable=self.resultFile)

        self.resultColumn = tk.StringVar(master)
        edit = self.builder.get_object('Entry_ResultColumn')
        edit.config(textvariable=self.resultColumn)

        self.progress = tk.DoubleVar(master)
        self.progressbar = self.builder.get_object('Progressbar_1')
        self.progressbar.config(variable=self.progress)

    def on_close_clicked(self):
        self.mainwindow.quit()

    def on_load_file_class1(self):
        self.fileC1.set(filedialog.askopenfilename())

    def on_load_file_class2(self):
        self.fileC2.set(filedialog.askopenfilename())

    def on_load_file_rules(self):
        self.rulesFile.set(filedialog.askopenfilename())

    def on_load_dataFile(self):
        self.dataFile.set(filedialog.askopenfilename())

    def on_load_result_file(self):
        self.resultFile.set(filedialog.askopenfilename())

    def on_make_rules(self):
        if makerulesfile(self.fileC1.get(), self.fileC2.get(), self.rulesFile.get(), self.c1.get(), self.c2.get()):
            messagebox.showinfo('Make Rules','Rules file created with success')
        else:
            messagebox.showerror('Make Rules', 'Error making rules files')

    def on_classify(self):

        msg = analysefile(self.dataFile.get(),self.rulesFile.get(),self.resultFile.get(),self.resultColumn.get())
        if msg:
            messagebox.showinfo('Classify', 'Result file created with success\n%s' % msg)
        else:
            messagebox.showerror('Classify', 'Error making result files!')

    def on_make_rules_and_tests(self):
        self.progressbar["maximum"] = 50.0
        self.progress.set(0.0)
        fname = maketests(self.fileC1.get(), self.fileC2.get(), self.rulesFile.get(), self.c1.get(), self.c2.get(), self.progress, self.master)
        if fname:
            messagebox.showinfo('Tests', 'Test finished with success\nFile %s created.' % fname)
        else:
            messagebox.showerror('Tests', 'Error making tests!')


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)
    root.winfo_toplevel().title('Binary Classify')
    root.resizable(False, False)
    root.mainloop()