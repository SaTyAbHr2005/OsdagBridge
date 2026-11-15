"""Build a sample OsdagBridge design report without clicking through the GUI.

The script opens the real application window, enters the main inputs, runs
Design and then Generate Report, so the PDF goes through exactly the same code
a user's report does. Running it twice with the same arguments gives the same
inputs, which makes it suitable for before/after comparisons of report changes.

    python tools/build_sample_report.py sample_report.pdf
    python tools/build_sample_report.py out.pdf --span 35 --carriageway 11 --preview
    python tools/build_sample_report.py out.pdf --keep-build build/ --set-input "loading.live_load.irc_class_a=true"

Everything runs inside main(): the app's loading spinner starts a
multiprocessing child, and on Windows that child re-imports this file.
"""
import argparse
import json
import os
import sys
import time

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src")
TIMEOUT_S = 20 * 60


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("output", help="PDF file to write")
    parser.add_argument("--span", default="30", help="span in m (default 30)")
    parser.add_argument("--carriageway", default="7.5", help="carriageway width in m (default 7.5)")
    parser.add_argument("--state", default="Maharashtra", help="project location state")
    parser.add_argument("--district", default="Mumbai", help="project location district")
    parser.add_argument("--preview", action="store_true", help="build as the Preview PDF button does")
    parser.add_argument("--keep-build", metavar="DIR",
                        help="keep the LaTeX build (.tex, .log, images) in DIR")
    parser.add_argument("--main-input", metavar="KEY=VALUE", action="append", default=[],
                        help="set a main-page field before Design, e.g. geometry.footpath=Both Sides "
                             "or geometry.skew_angle=10; may be repeated")
    parser.add_argument("--set-input", metavar="KEY=JSON", action="append", default=[],
                        help="change a backend input after Design and before the report, e.g. a "
                             "Loading tab selection that only the report reads; may be repeated")
    return parser.parse_args()


def main():
    args = _parse_args()
    out_pdf = os.path.abspath(args.output)
    overrides = {}
    for item in args.set_input:
        key, _, value = item.partition("=")
        overrides[key] = json.loads(value)

    sys.path.insert(0, os.path.abspath(SRC_DIR))
    # Importing the app's entry module runs its DLL and database setup without starting it.
    import osdagbridge.desktop.__main__ as app_main
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QLineEdit
    from osdagbridge.desktop.ui.dialogs import custom_messagebox, project_location, report_options

    if args.keep_build:
        import contextlib
        import types
        from osdagbridge.core.reports import report_generator

        @contextlib.contextmanager
        def _kept_dir(*_a, **_kw):
            os.makedirs(args.keep_build, exist_ok=True)
            yield os.path.abspath(args.keep_build)

        # The report builds in tempfile.TemporaryDirectory(); give only the report
        # module a version that keeps the folder, leaving the stdlib untouched.
        report_generator.tempfile = types.SimpleNamespace(TemporaryDirectory=_kept_dir)

    # Message boxes would block an unattended run; print them instead.
    box_init = custom_messagebox.CustomMessageBox.__init__

    def box_init_keep_text(self, title="Message", text="Message", *a, **kw):
        self._sample_text = f"{title} | {text}"
        box_init(self, title, text, *a, **kw)

    def print_box(self):
        print(f"[sample-report] message: {self._sample_text}")
        return 0

    custom_messagebox.CustomMessageBox.__init__ = box_init_keep_text
    custom_messagebox.CustomMessageBox.exec = print_box

    def pick_location(self):
        self.state_combo.setCurrentText(args.state)
        options = [self.district_combo.itemText(i) for i in range(self.district_combo.count())]
        pick = next((o for o in options if args.district.lower() in o.lower()),
                    next((o for o in options if not o.lower().startswith("select")), ""))
        self.district_combo.setCurrentText(pick)
        if args.district.lower() not in pick.lower():
            print(f"[sample-report] district {args.district!r} not found in {args.state}; using {pick!r}")
        self.validate_and_save()
        return self.result()

    project_location.ProjectLocationDialog.exec = pick_location

    def fill_report_form(self):
        self.project_name.setText("OsdagBridge Sample")
        self.designer.setText("OsdagBridge")
        self.request = self.build_request(out_pdf, preview=args.preview)
        self.is_preview = False          # do not open the PDF viewer
        return QDialog.DialogCode.Accepted

    report_options.ReportOptionsDialog.exec = fill_report_form

    app = QApplication(sys.argv)
    app.setStyleSheet(app_main.load_stylesheet())
    window = app_main.CustomWindow("OsdagBridge", app_main.PlateGirderBridge)
    window.showMaximized()

    if os.path.exists(out_pdf):
        os.remove(out_pdf)
    state = {"phase": "design", "t0": time.time()}

    def tick():
        if time.time() - state["t0"] > TIMEOUT_S:
            print("[sample-report] timed out")
            app.exit(2)
        elif state["phase"] == "design":
            dock = window.input_dock
            dock.show_project_location_dialog()
            fields = [("geometry.span", args.span), ("geometry.carriageway_width", args.carriageway)]
            fields += [item.split("=", 1) for item in args.main_input]
            for key, value in fields:
                widget = dock._w(key)
                if isinstance(widget, QComboBox):
                    widget.setCurrentText(value)
                elif isinstance(widget, QLineEdit):
                    widget.setText(value)
                    widget.editingFinished.emit()
                else:
                    print(f"[sample-report] no main-page field {key!r}")
                    app.exit(1)
                    return
                print(f"[sample-report] {key} = {window.input_dict.get(key)}")
            print("[sample-report] running Design")
            state["phase"] = "designing"
            window.common_design_func("Design")
        elif state["phase"] == "designing" and not getattr(window, "_design_running", False):
            if not window.input_dock.is_locked:
                print("[sample-report] Design did not finish; see the messages above")
                app.exit(1)
                return
            # The report reads the backend's own copy of the inputs.
            window.backend.input_dict.update(overrides)
            print("[sample-report] generating the report")
            state["phase"] = "reporting"
            window.output_dock._on_report_clicked()
        elif state["phase"] == "reporting" and os.path.exists(out_pdf):
            print(f"[sample-report] saved {out_pdf}")
            QTimer.singleShot(3000, app.quit)       # let the report worker finish copying
            state["phase"] = "done"

    timer = QTimer()
    timer.timeout.connect(tick)
    QTimer.singleShot(4000, lambda: timer.start(2000))     # give the window time to settle
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
