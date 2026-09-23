import json, os, threading, tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

from .config import Config, ROOT, DATA, QUARANTINE, LOCALIZATION
from .localization import I18N
from .storage.jsondb import JSONDB
from .storage.quarantine import Quarantine
from .engine.scanner import Scanner
from .engine.analyzer import analyze
from .protection.realtime import RealtimeMonitor

class MaxGuardApp:
    def __init__(self):
        self.config = Config()
        self.i18n = I18N(LOCALIZATION)
        if self.config.data.get("language") is None:
            self._choose_language()
        else:
            self.i18n.load(self.config.data["language"])

        self.root = tk.Tk()
        self.root.title(self.i18n.t("app_title"))
        self.root.geometry("1120x720")
        self.root.minsize(980, 620)
        self.style = ttk.Style(self.root)
        try: self.style.theme_use("clam")
        except tk.TclError: pass

        self.dbs = {
            "history": JSONDB(DATA/"history.json"),
            "threats": JSONDB(DATA/"threats.json"),
            "signatures": JSONDB(DATA/"signatures.json"),
            "trusted": JSONDB(DATA/"trusted_hashes.json")
        }
        self.quarantine = Quarantine(QUARANTINE)
        self.stop_requested = False
        self.last_results = []
        self.monitor = None
        initial_status = self.i18n.t("protection_on") if self.config.data.get("realtime") else self.i18n.t("protection_off")
        self.status_var = tk.StringVar(value=initial_status)
        self.progress_var = tk.DoubleVar(value=0)
        self.page = None

        self._build()
        self._show_dashboard()
        self._start_realtime_if_enabled()

    def _choose_language(self):
        win = tk.Tk()
        win.title("MaxGuard")
        win.geometry("360x220")
        win.resizable(False, False)
        ttk.Label(win, text="MaxGuard 1.0", font=("Segoe UI", 18, "bold")).pack(pady=(24,8))
        ttk.Label(win, text="Choose language / Оберіть мову / Elige idioma").pack(pady=4)
        value = tk.StringVar(value="en")
        combo = ttk.Combobox(win, textvariable=value, state="readonly",
                             values=["en","uk","es"], width=22)
        combo.pack(pady=12)
        def save():
            self.config.data["language"] = value.get()
            self.config.save()
            win.destroy()
        ttk.Button(win, text="Continue", command=save).pack(pady=10)
        win.mainloop()
        self.i18n.load(self.config.data.get("language") or "en")

    def _build(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        top = ttk.Frame(self.root, padding=(18,12))
        top.grid(row=0,column=0,columnspan=2,sticky="ew")
        top.columnconfigure(1, weight=1)
        ttk.Label(top,text="🛡 MAXGUARD",font=("Segoe UI",20,"bold")).grid(row=0,column=0,sticky="w")
        ttk.Label(top,textvariable=self.status_var,font=("Segoe UI",11)).grid(row=0,column=1,sticky="e")

        side = ttk.Frame(self.root,padding=(14,8))
        side.grid(row=1,column=0,sticky="nsw")
        buttons = [
            ("dashboard", self._show_dashboard),
            ("scanner", self._show_scanner),
            ("threat_center", self._show_threats),
            ("quarantine", self._show_quarantine),
            ("history", self._show_history),
            ("signatures", self._show_signatures),
            ("trusted_hashes", self._show_trusted),
            ("settings", self._show_settings),
            ("activity", self._show_activity),
        ]
        for key, cmd in buttons:
            ttk.Button(side,text=self.i18n.t(key),command=cmd,width=20).pack(pady=4)

        self.content = ttk.Frame(self.root,padding=(10,8))
        self.content.grid(row=1,column=1,sticky="nsew")
        self.content.rowconfigure(1,weight=1)
        self.content.columnconfigure(0,weight=1)

    def _clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def _title(self, text):
        self._clear()
        ttk.Label(self.content,text=text,font=("Segoe UI",22,"bold")).grid(row=0,column=0,sticky="w",pady=(0,14))

    def _show_dashboard(self):
        self._title(self.i18n.t("dashboard"))
        frame = ttk.Frame(self.content)
        frame.grid(row=1,column=0,sticky="nsew")
        frame.columnconfigure((0,1,2),weight=1)
        stats = [
            ("status", self.i18n.t("protection_on") if self.config.data["realtime"] else self.i18n.t("protection_off")),
            ("files_scanned", str(len(self.dbs["history"].read([])))),
            ("threats_found", str(len(self.dbs["threats"].read([]))))
        ]
        for i,(a,b) in enumerate(stats):
            box=ttk.LabelFrame(frame,text=self.i18n.t(a),padding=18)
            box.grid(row=0,column=i,sticky="nsew",padx=6)
            ttk.Label(box,text=b,font=("Segoe UI",15,"bold")).pack()
        scanbox=ttk.LabelFrame(frame,text=self.i18n.t("scanner"),padding=18)
        scanbox.grid(row=1,column=0,columnspan=3,sticky="ew",pady=18)
        ttk.Button(scanbox,text=self.i18n.t("quick_scan"),command=self.quick_scan).pack(side="left",padx=5)
        ttk.Button(scanbox,text=self.i18n.t("full_scan"),command=self.full_scan).pack(side="left",padx=5)
        ttk.Button(scanbox,text=self.i18n.t("custom_scan"),command=self.custom_scan).pack(side="left",padx=5)

    def _show_scanner(self):
        self._title(self.i18n.t("scanner"))
        box=ttk.Frame(self.content)
        box.grid(row=1,column=0,sticky="nsew")
        box.columnconfigure(0,weight=1); box.rowconfigure(1,weight=1)
        actions=ttk.Frame(box); actions.grid(row=0,column=0,sticky="ew",pady=4)
        for txt,cmd in [(self.i18n.t("quick_scan"),self.quick_scan),(self.i18n.t("full_scan"),self.full_scan),(self.i18n.t("custom_scan"),self.custom_scan)]:
            ttk.Button(actions,text=txt,command=cmd).pack(side="left",padx=4)
        ttk.Button(actions,text=self.i18n.t("stop"),command=self.stop_scan).pack(side="left",padx=4)
        self.progress=ttk.Progressbar(box,variable=self.progress_var,maximum=100)
        self.progress.grid(row=1,column=0,sticky="ew",pady=8)
        self.results=ttk.Treeview(box,columns=("status","risk","confidence","path"),show="headings")
        for c,t in [("status",self.i18n.t("status")),("risk",self.i18n.t("risk")),("confidence",self.i18n.t("confidence")),("path",self.i18n.t("path"))]:
            self.results.heading(c,text=t); self.results.column(c,width=110 if c!="path" else 620)
        self.results.grid(row=2,column=0,sticky="nsew")
        box.rowconfigure(2,weight=1)
        self._scanner_ready=True

    def _show_threats(self):
        self._title(self.i18n.t("threat_center"))
        self._table(["status","risk","path"], self.dbs["threats"].read([]))

    def _show_history(self):
        self._title(self.i18n.t("history"))
        self._table(["status","risk","path"], self.dbs["history"].read([]))

    def _show_activity(self):
        self._title(self.i18n.t("activity"))
        txt=tk.Text(self.content,wrap="word")
        txt.grid(row=1,column=0,sticky="nsew")
        for item in self.dbs["history"].read([])[-200:]:
            txt.insert("end", f'{item.get("time","")}  {item.get("status","")}  {item.get("path","")}\n')
        txt.configure(state="disabled")

    def _table(self, columns, rows):
        wrap=ttk.Frame(self.content); wrap.grid(row=1,column=0,sticky="nsew")
        wrap.rowconfigure(0,weight=1); wrap.columnconfigure(0,weight=1)
        tree=ttk.Treeview(wrap,columns=columns,show="headings")
        for c in columns:
            tree.heading(c,text=self.i18n.t(c) if c in self.i18n.data else c.title())
            tree.column(c,width=150 if c!="path" else 700)
        for r in rows:
            tree.insert("","end",values=[r.get(c,"") for c in columns])
        tree.grid(row=0,column=0,sticky="nsew")
        sb=ttk.Scrollbar(wrap,orient="vertical",command=tree.yview); sb.grid(row=0,column=1,sticky="ns")
        tree.configure(yscrollcommand=sb.set)

    def _show_quarantine(self):
        self._title(self.i18n.t("quarantine"))
        wrap=ttk.Frame(self.content); wrap.grid(row=1,column=0,sticky="nsew")
        tree=ttk.Treeview(wrap,columns=("id","original","time"),show="headings")
        for c,t in [("id","ID"),("original",self.i18n.t("path")),("time","Time")]:
            tree.heading(c,text=t); tree.column(c,width=180 if c!="original" else 650)
        for x in self.quarantine.items(): tree.insert("","end",values=(x["id"],x["original"],x["time"]))
        tree.pack(fill="both",expand=True)
        btn=ttk.Frame(wrap); btn.pack(fill="x",pady=8)
        def restore():
            sel=tree.selection()
            if sel:
                token=tree.item(sel[0])["values"][0]
                self.quarantine.restore(token); self._show_quarantine()
        def delete():
            sel=tree.selection()
            if sel:
                token=tree.item(sel[0])["values"][0]
                if messagebox.askyesno("MaxGuard", self.i18n.t("delete")+"?"):
                    self.quarantine.delete(token); self._show_quarantine()
        ttk.Button(btn,text=self.i18n.t("restore"),command=restore).pack(side="left",padx=4)
        ttk.Button(btn,text=self.i18n.t("delete"),command=delete).pack(side="left",padx=4)

    def _show_signatures(self):
        self._title(self.i18n.t("signatures"))
        data=self.dbs["signatures"].read([])
        txt=tk.Text(self.content,wrap="none")
        txt.grid(row=1,column=0,sticky="nsew")
        txt.insert("1.0","\n".join(data) if data else self.i18n.t("no_results"))
        ttk.Button(self.content,text=self.i18n.t("clear"),command=lambda:self._clear_signatures(txt)).grid(row=2,column=0,sticky="w",pady=5)

    def _clear_signatures(self, txt):
        if messagebox.askyesno("MaxGuard", self.i18n.t("clear")+"?"):
            self.dbs["signatures"].write([]); txt.delete("1.0","end")

    def _show_trusted(self):
        self._title(self.i18n.t("trusted_hashes"))
        data=self.dbs["trusted"].read([])
        txt=tk.Text(self.content,wrap="none"); txt.grid(row=1,column=0,sticky="nsew")
        txt.insert("1.0","\n".join(data) if data else self.i18n.t("no_results"))

    def _show_settings(self):
        self._title(self.i18n.t("settings"))
        box=ttk.Frame(self.content); box.grid(row=1,column=0,sticky="nw")
        lang=tk.StringVar(value=self.config.data.get("language","en"))
        ttk.Label(box,text=self.i18n.t("language")).grid(row=0,column=0,sticky="w",pady=8)
        ttk.Combobox(box,textvariable=lang,state="readonly",values=["en","uk","es"],width=18).grid(row=0,column=1,padx=8)
        heur=tk.BooleanVar(value=self.config.data["heuristics"])
        arc=tk.BooleanVar(value=self.config.data["scan_archives"])
        auto=tk.BooleanVar(value=self.config.data["auto_quarantine"])
        rt=tk.BooleanVar(value=self.config.data["realtime"])
        ttk.Checkbutton(box,text=self.i18n.t("heuristics"),variable=heur).grid(row=1,column=0,columnspan=2,sticky="w")
        ttk.Checkbutton(box,text=self.i18n.t("archives"),variable=arc).grid(row=2,column=0,columnspan=2,sticky="w")
        ttk.Checkbutton(box,text=self.i18n.t("auto_quarantine"),variable=auto).grid(row=3,column=0,columnspan=2,sticky="w")
        ttk.Checkbutton(box,text=self.i18n.t("protection_on"),variable=rt).grid(row=4,column=0,columnspan=2,sticky="w")
        def save():
            self.config.data.update(language=lang.get(),heuristics=heur.get(),scan_archives=arc.get(),
                                    auto_quarantine=auto.get(),realtime=rt.get())
            self.config.save()
            self.i18n.load(lang.get())
            if rt.get(): self._start_realtime_if_enabled()
            else:
                if self.monitor: self.monitor.stop()
            messagebox.showinfo("MaxGuard","Settings saved. Restart MaxGuard to fully refresh the interface language.")
        ttk.Button(box,text=self.i18n.t("save"),command=save).grid(row=5,column=0,pady=14,sticky="w")

    def _start_realtime_if_enabled(self):
        paths=self.config.data.get("realtime_paths") or [str(Path.home()/"Downloads"),str(Path.home()/"Desktop")]
        if self.config.data.get("realtime"):
            self.monitor=RealtimeMonitor(paths,self._on_realtime_file); self.monitor.start()

    def _on_realtime_file(self, path):
        def work():
            r=analyze(path,self.dbs["signatures"].read([]),self.dbs["trusted"].read([]),
                       self.config.data["heuristics"],self.config.data["scan_archives"],self.config.data["sample_size_mb"])
            self.root.after(0,lambda:self._handle_result(r))
        threading.Thread(target=work,daemon=True).start()

    def _handle_result(self,r):
        self.last_results.append(r)
        hist=self.dbs["history"].read([])
        r2=dict(r); r2["time"]=datetime.now().isoformat(timespec="seconds")
        hist.append(r2); self.dbs["history"].write(hist[-5000:])
        if r["status"] in {"THREAT","CRITICAL","HIGH RISK"}:
            threats=self.dbs["threats"].read([]); threats.append(r2); self.dbs["threats"].write(threats[-2000:])
            if r["status"]=="THREAT" and self.config.data["auto_quarantine"]:
                self.quarantine.put(r["path"])
        if hasattr(self,"results"):
            self.results.insert("","end",values=(r["status"],r["risk"],r["confidence"],r["path"]))
        self.status_var.set(f'{r["status"]}: {r["path"]}')

    def _scan(self, paths):
        self._show_scanner()
        self.progress_var.set(0)
        def on_result(r): self.root.after(0,lambda rr=r:self._handle_result(rr))
        def on_progress(done,total):
            pct=0 if total==0 else done/total*100
            self.root.after(0,lambda p=pct:self.progress_var.set(p))
        scanner=Scanner(self.config,self.dbs,on_result,on_progress)
        self.current_scanner=scanner
        def work():
            n=scanner.scan(paths)
            self.root.after(0,lambda:self.status_var.set(f"{self.i18n.t('scan_complete')}: {n}"))
        threading.Thread(target=work,daemon=True).start()

    def quick_scan(self):
        paths=[str(Path.home()/x) for x in ("Desktop","Downloads","Documents") if (Path.home()/x).exists()]
        self._scan(paths)

    def full_scan(self):
        self._scan([str(Path.home())])

    def custom_scan(self):
        p=filedialog.askdirectory(title=self.i18n.t("select_folder"))
        if p: self._scan([p])

    def stop_scan(self):
        if hasattr(self,"current_scanner"):
            self.current_scanner.stop()
        self.status_var.set(self.i18n.t("stop"))

    def run(self):
        self.root.mainloop()
