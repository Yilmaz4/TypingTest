from tkinter import *
from tkinter import font
tkEntry = Entry
from tkinter.ttk import *
from random import shuffle, choice
from difflib import SequenceMatcher

import time, Levenshtein

comments = {
    0:   ["immeasurable speed!", "ZeroDivisionError", "amazing", "I hope this wasn't intentional"],
    1:   ["dude you didn't even try", "absolute dogshit", "n00b", "this ain't for u", "so fucking slow", "I'd rather watch paint dry than you type", "almost slept while waiting for you"],
    20:  ["ok you're new to this", "you'll get better", "bad", "below average yknow", "you- you aren't using a single finger to type.... right?"],
    40:  ["mid", "average", "meh", "good enough ig", "chcek out 10 finger typing or smth"],
    60:  ["not bad", "above average", "good, just good", "nice try"],
    80:  ["very good", "you've got potential", "congrats", "fluent"],
    101: ["above 100, damn", "you're about as fast as I am", "professional", "very fluent", "fast enough for anything"],
    130: ["you're faster than me, respect", "absolutely professional", "a little too fast", "no need for this speed, really"],
    170: ["dude wtf", "do something more productive with that speed", "get a life", "touch some grass", "jesus", "really, too fast for a human"],
    200: ["nah you're hacking, tell me how u did it tho", "no fking way", "twice my speed, how", "if this is real, u seriously need to take a break"]
}

dark_mode = 1
levenshtein = 1

class Interface(Tk):
    def __init__(self):
        super().__init__()
        self.wm_title("Offline Typing Test")
        self.wm_geometry("650x113")
        self.wm_resizable(False, False)
        
        self.duration = IntVar(value=60)
        self.theme = IntVar(value=1)
        self.font = StringVar(value="Consolas")
        self.showWPM = IntVar(value=1)
        self.flash = IntVar(value=1)
        self.algorithm = IntVar(value=2)
        self.textType = IntVar(value=1)
        
        self.last_reset = time.time() - 1
        
        self.reset()
        self.init_ui()
    
    def init_ui(self):
        self.configure(background="#202020" if dark_mode else "#f0f0f0")
        
        self.time = Label(self, text="Time remaining: 1:00", background="#202020" if dark_mode else "#f0f0f0", foreground="white" if dark_mode else "black")
        self.time.place(x=9, y=6)
        self.wpml = Label(self, text="WPM: Pending", background="#202020" if dark_mode else "#f0f0f0", foreground="white" if dark_mode else "black")
        self.wpml.place(x=150, y=6)
        
        self.text = Text(self, background="#202020" if dark_mode else "#f0f0f0", foreground="white" if dark_mode else "black", borderwidth=0, font=(self.font.get(), 12), wrap=WORD, state="normal")
        self.text.place(x=10, y=30, height=40, width=630)
        self.text.insert("1.0", ' '.join(self.txt))
        self.text.tag_add("current", "1.0", f"1.{len(self.word)}")
        self.text.tag_config("current", background="#0064d7" if dark_mode else "yellow", foreground="white" if dark_mode else "black", font=(self.font.get(), 12))
        self.text.tag_config("misspelled", background="red", foreground="white", font=(self.font.get(), 12, "bold"))
        
        self.input = StringVar(self)
        self.entry = tkEntry(self, textvariable=self.input, font=(self.font.get(), 12), validate='all', 
                           validatecommand = (self.register(lambda c: c != ' '), '%P'),
                           background="#363636" if dark_mode else "white", foreground="white" if dark_mode else "black", relief="flat" if dark_mode else "groove")
        self.entry.place(x=10, y=75, width=630)
        self.input.trace_add("write", self.validate)
        self.entry.bind("<space>",  self.advance, str())
        self.entry.bind("<BackSpace>", self.on_backspace, str())
        self.entry.focus_set()
    
    def generate_text(self):
        if self.textType.get():
            with open("texts.txt", mode='r') as f:
                words = f.read().split(' ')
                return words
        else:
            with open("words.txt", mode="r") as f:
                words = f.read().split('|')
                shuffle(words)
                return words
    
    def settings(self):
        # duration
        # text generation algorithm (shuffle/generate)
        
        class Settings(Toplevel):
            def __init__(self, master: Interface):
                super().__init__(master)
                self.root = master
                
                self.wm_title("Settings")
                self.wm_geometry("400x400")
                self.wm_resizable(False, False)
                
                Label(self, text="Appearance", font=("Segoe UI", 18, "bold")).place(x=10, y=0)
                
                themeFrame = LabelFrame(self, text="Theme")
                themeFrame.place(x=10, y=40, height=70, width=175)
                self.lightmode = Radiobutton(themeFrame, text="Light mode", value=0, variable=self.root.theme, takefocus=0, command=self.root.toggle_theme)
                self.darkmode  = Radiobutton(themeFrame, text="Dark mode", value=1, variable=self.root.theme, takefocus=0, command=self.root.toggle_theme)
                self.lightmode.place(x=5, y=1)
                self.darkmode.place(x=5, y=23)
                
                def on_fontSelect(*args, **kwargs):
                    font = self.root.font.get()
                    self.fontSelect.configure(font=(font, 9))
                    self.root.text.configure(font=(font, 12))
                    self.root.entry.configure(font=(font, 12))
                    self.root.text.tag_config("current", font=(font, 12))
                    self.root.text.tag_config("misspelled", font=(font, 12, "bold"))
                def on_WPMShowCheck():
                    if self.root.showWPM.get():
                        self.root.wpml = Label(self.root, text="WPM: Pending", background="#202020" if dark_mode else "#f0f0f0", foreground="white" if dark_mode else "black")
                        self.root.wpml.place(x=150, y=6)
                    else:
                        self.root.wpml.destroy()
                fontValues = list(font.families())
                fontValues.sort()
                
                Label(self, text="Font:").place(x=195, y=40)
                self.fontSelect = Combobox(self, state="readonly", textvariable=self.root.font, font=(self.root.font.get(), 9), values=fontValues, takefocus=0)
                self.fontSelect.bind('<<ComboboxSelected>>', on_fontSelect)
                self.fontSelect.place(x=230, y=40, width=160)
                
                self.showWPMCheck = Checkbutton(self, text="Show WPM while typing", variable=self.root.showWPM, takefocus=0, command=on_WPMShowCheck)
                self.showWPMCheck.place(x=195, y=67)
                
                self.flashTimerCheck = Checkbutton(self, text="Flash timer when 5 seconds left", variable=self.root.flash, takefocus=0)
                self.flashTimerCheck.place(x=195, y=91)
                
                Label(self, text="General", font=("Segoe UI", 18, "bold")).place(x=10, y=110)
                
                algorithmFrame = LabelFrame(self, text="Spelling similarity detection algorithm", takefocus=0)
                algorithmFrame.place(x=10, y=150, height=90, width=380)
                self.algorithmNone = Radiobutton(algorithmFrame, text="None (misspelled words will not be counted)", value=0, variable=self.root.algorithm, takefocus=0)
                self.algorithmRatcliff = Radiobutton(algorithmFrame, text="Ratcliff/Obershelp", value=1, variable=self.root.algorithm, takefocus=0)
                self.algorithmLevenshtein = Radiobutton(algorithmFrame, text="Levenshtein (recommended)", value=2, variable=self.root.algorithm, takefocus=0)
                
                self.algorithmNone.place(x=5, y=1)
                self.algorithmRatcliff.place(x=5, y=23)
                self.algorithmLevenshtein.place(x=5, y=45)
                
                self.focus_force()
                self.transient(master)
                
        self.settingsUI = Settings(self)
        self.settingsUI.mainloop()
        
    def toggle_theme(self):
        if str(self.entry["state"]) == DISABLED:
            self.reset()
        global dark_mode
        dark_mode = not bool(dark_mode)
        for widget in [w for w in self.winfo_children() if isinstance(w, (Label, Text, Entry, tkEntry))]:
            widget.destroy()
        self.init_ui()
        self.settingsUI.focus_force()
        
    def results(self):
        self.text.place_forget()
        self.entry.place_forget()
        try:
            self.wpml.place_forget()
        except: pass
        self.time.place_forget()
        
        self.continueLabel = Label(self, text="Press Enter to continue...", font=("Impact", 33, "italic"), background="#282828", foreground="#252525")
        self.continueLabel.place(x=175, y=25)
        
        wpm = int((self.idx1 - self.errors) // ((self.duration.get() - self.timer) / 60))
        
        self.result = Label(self, text="WPM: " + str(wpm), font=("Segoe UI", 20, "bold"), background="#202020" if dark_mode else "#f0f0f0", foreground="white" if dark_mode else "black")
        self.result.place(x=10, y=10)
        
        self.accuracy = Label(self, text="Accuracy: " + (str(100 - (100 * self.errors) // self.idx1) + "%" if self.idx1 else "Nope"), font=("Segoe UI", 14), background="#202020" if dark_mode else "#f0f0f0", foreground="white" if dark_mode else "black")
        self.accuracy.place(x=10, y=45)
        
        self.comment = Label(self, font=("Segoe UI", 9), background="#202020" if dark_mode else "#f0f0f0", foreground="white" if dark_mode else "black")
        self.comment.place(x=10, y=75)
        if wpm == 69:
            self.comment.configure(text="nice")
        for k, v in list(comments.items())[::-1]:
            if wpm >= k:
                self.comment.configure(text=f"\"{choice(v)}\"")
                break
        self.bind("<Return>", self.reset)
        self.unbind("<Control_L>r")
        
    def countdown(self):
        if not self.begun:
            return
        if not self.timer:
            self.entry.configure(state=DISABLED)
            self.results()
            return
        self.timer -= 1
        self.time.configure(text=f"Time remaining: 0:{('0' if self.timer <= 9 else '') + str(self.timer)}",
            foreground=("white" if dark_mode else "black") if self.timer > 5 or self.flash.get() == 0 else ("red" if self.timer % 2 == 0 else "white" if dark_mode else "black"))
        self.countdown_after = self.after(1000, self.countdown)
        
    def update_wpm(self):
        if self.showWPM.get() and self.timer != self.duration.get():
            self.wpml.configure(text=f"WPM: {int((self.idx1 - self.errors) // ((self.duration.get() - self.timer) / 60))}")
        self.update_wpm_after = self.after(50, self.update_wpm)
    
    def advance(self, *args, **kwargs):
        if not self.input.get():
            return
        self.text.tag_remove("current", f"1.{self.idx2}", f"1.{self.idx2 + len(self.word)}")
        if self.input.get() != self.word:
            if not self.algorithm.get():
                diff = 0
            elif self.algorithm.get() == 1:
                diff = SequenceMatcher(None, self.input.get(), self.word).ratio()
            else:
                diff = Levenshtein.ratio(self.input.get(), self.word)
            self.errors += (1 - diff)
            self.text.tag_add("misspelled", f"1.{self.idx2}", f"1.{self.idx2 + len(self.word)}")
        self.entry.delete(0, END)
        self.idx1 += 1
        self.catl += 1
        self.idx2 += len(self.word) + 1
        self.word = self.txt[self.idx1]
        self.text.tag_add("current", f"1.{self.idx2}", f"1.{self.idx2 + len(self.word)}")
        self.text.tag_config("current", background="#0064d7" if dark_mode else "yellow")
        self.text.update()
        
        n = 0
        for i in range(self.iatl, len(self.txt)):
            if font.Font(family=self.font.get(), size=12).measure(' '.join(self.txt[self.iatl:i])) > 630:
                n = i - 1
                break
        if self.catl == n - self.iatl:
            self.text.yview_scroll(1, "units")
            self.line += 1
            self.iatl = self.idx1
            self.catl = 0
    
    def on_backspace(self, *args, **kwargs):
        self.backspaces += 1
        
    def validate(self, *args, **kwargs):
        if not self.begun:
            self.begun = True
            self.countdown_after  = self.after(1000, self.countdown)
            self.update_wpm_after = self.after(50, self.update_wpm)
        correct = True
        if len(self.input.get()) > len(self.word):
            correct = False
        for i in range(min(len(self.word), len(self.input.get()))):
            if self.input.get()[i] != self.word[i]:
                self.missed_keys.append(self.input.get()[i])
                correct = False
                break
        if not correct:
            self.mispresses += 1
        self.text.tag_config("current", background=("#0064d7" if dark_mode else "yellow") if correct else "red")
    
    def reset(self, *args, **kwargs):
        self.unbind("<Return>")
        self.bind("<Control_L>r", self.reset)
        if time.time() - 1 < self.last_reset:
            return
        self.last_reset = time.time()
        
        self.txt = self.generate_text()
        
        self.idx1 = 0
        self.idx2 = 0
        self.line = 0
        self.iatl = 0
        self.catl = 0
        self.word = self.txt[self.idx1]
        
        self.errors = 0
        self.mispresses = 0
        self.backspaces = 0
        
        self.missed_keys = []
        
        self.begun = False
        self.timer = self.duration.get()
        
        try:
            self.time.configure(text="Time remaining: 1:00")
            self.wpml.configure(text="WPM: Pending")
            self.text.yview_moveto(0)
            self.text.delete("1.0", "end")
            self.text.insert("1.0", ' '.join(self.txt))
            self.text.tag_remove("misspelled", "1.0", "end")
            self.text.tag_remove("current", "1.0", "end")
            self.text.tag_add("current", "1.0", f"1.{len(self.word)}")
            self.text.tag_config("current", background="#0064d7" if dark_mode else "yellow")
            
            self.entry.delete(0, END)

            if str(self.entry["state"]) != NORMAL:
                self.result.place_forget()
                self.accuracy.place_forget()
                self.comment.place_forget()
                self.continueLabel.place_forget()
                self.time.place(x=9, y=6)
                self.wpml.place(x=150, y=6)
                self.text.place(x=10, y=30, height=40, width=630)
                self.entry.place(x=10, y=75, width=630)
                self.entry.delete(0, END)
                self.input.set('')
                self.entry.configure(state=NORMAL)
            self.time.configure(foreground="white" if dark_mode else "black")
            self.after_cancel(self.countdown_after)
            self.after_cancel(self.update_wpm_after)
            self.begun = False
        except: pass
        
if __name__ == "__main__":
    Interface().mainloop()