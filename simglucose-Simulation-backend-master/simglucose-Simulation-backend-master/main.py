import time
from typing import Dict, List, Tuple

import keyboard
from threading import Timer

import dearpygui.dearpygui as dpg

from AiPatient.AiPatient import AiPatient
from Patient import Patient
from SimulationClock import SimulationClock
from shapes import Circle, PhoneShape, Rectangle, ShapeConnection


# ----------------------------
# Constants and Utilities
# ----------------------------
HYPO_THRESHOLD = 70
HYPER_THRESHOLD = 180


def log_msg(message: str) -> None:
    current_logs = dpg.get_value("log_text")
    dpg.set_value("log_text", current_logs + message + "\n")


def seconds_to_ddhhmm(seconds: float) -> List[int]:
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    return [days, hours, minutes]


# ----------------------------
# Carb Intake UI Callbacks
# ----------------------------
def open_carb_modal(sender, app_data, user_data) -> None:  # noqa: ARG001
    dpg.configure_item("carb-modal", show=True)


def cancel_carb_modal(sender, app_data, user_data) -> None:  # noqa: ARG001
    dpg.configure_item("carb-modal", show=False)


def confirm_carb_intake(sender, app_data, patient) -> None:  # user_data = patient
    try:
        grams_val = dpg.get_value("carb-input")
        grams = float(grams_val) if grams_val is not None else 0.0
    except Exception:
        grams = 0.0

    if grams <= 0:
        dpg.configure_item("carb-modal", show=False)
        return

    if hasattr(patient, "addCarbIntake"):
        patient.addCarbIntake(grams)  # type: ignore[attr-defined]
        log_msg(f"Queued carb intake: {grams:.0f} g for next model step")
    else:
        log_msg("Carb entry is available only in AI patient mode")

    dpg.set_value("carb-input", 0.0)
    dpg.configure_item("carb-modal", show=False)


# ----------------------------
# AI Patient Mode (standalone)
# ----------------------------
def ai_patient_loop() -> None:
    running = True
    patient = AiPatient()
    while running:
        if keyboard.is_pressed("q"):
            running = False
            break
        result = patient.simulateStep()
        print(f"{result}\n============\n")


class AiPatientAdapter:
    """Adapter to expose AiPatient with the same interface used by the UI.

    It keeps per-frame arrays aligned with `SimulationClock.getSimulationTimestampData()`
    by appending a value each UI tick, carrying forward last values between model steps.
    """

    STEP_SECONDS = 300  # 5 minutes per model step

    def __init__(self) -> None:
        self._ai = AiPatient()
        # Start time set on first external request via getSimStartTime()
        self._sim_start_time: int | None = None
        # Series data aligned with clock timestamps
        self._glucose_data: List[float] = []
        self._insulin_data: List[float] = []
        self._carb_data: List[float] = []
        # Latest values
        self._latest_glucose: float = float(self._ai._lastReadingsBuffer.iloc[-1]["glucose"])  # type: ignore[attr-defined]
        self._latest_insulin: float = 0.0
        self._latest_carbs: float = 0.0
        self._pending_carbs: float = 0.0
        # Step tracking
        self._last_step_sim_seconds: float = 0.0
        self._new_step_occurred: bool = False
        # Status
        self._last_risk: str | None = None

    # Interface expected by UI code
    def getPatientType(self) -> str:
        return "AI"

    def getSimStartTime(self) -> int:
        if self._sim_start_time is None:
            self._sim_start_time = int(time.time())
        return self._sim_start_time

    def getGlucoseLevelAtTimestamp(self, ts: int) -> float:
        # Rough lookup by step index; fallback to latest known value
        start = self.getSimStartTime()
        if ts <= start:
            return self._latest_glucose
        step_index = int((ts - start) // self.STEP_SECONDS)
        if 0 <= step_index < len(self._glucose_data):
            return float(self._glucose_data[step_index])
        return self._latest_glucose

    def updateGlucoseData(self, absoluteTimestamp: float) -> None:
        # Convert absolute to simulated seconds from start
        start = self.getSimStartTime()
        sim_seconds = max(0.0, float(absoluteTimestamp - start))
        self._new_step_occurred = False

        # First point: seed with initial glucose
        if not self._glucose_data:
            self._glucose_data.append(self._latest_glucose)
            return

        # Model step only every STEP_SECONDS; otherwise carry forward value
        if (sim_seconds - self._last_step_sim_seconds) >= self.STEP_SECONDS:
            # Apply any queued carbs at the model step
            result = self._ai.simulateStep(carbIntake=self._pending_carbs)
            self._latest_glucose = float(result["glucose"])  # type: ignore[index]
            self._latest_insulin = float(result["bolus"])    # type: ignore[index]
            self._latest_carbs = float(result["carbs"])      # type: ignore[index]
            self._last_step_sim_seconds = sim_seconds
            self._new_step_occurred = True
            # Clear pending carbs after applying this step
            self._pending_carbs = 0.0

        self._glucose_data.append(self._latest_glucose)

    def updateInsulinInjectionData(self, absoluteTimestamp: float) -> None:  # noqa: ARG002
        # Spike insulin only on new steps; zero otherwise
        self._insulin_data.append(self._latest_insulin if self._new_step_occurred else 0.0)

    def updateCarbIntakeData(self, absoluteTimestamp: float) -> None:  # noqa: ARG002
        self._carb_data.append(self._latest_carbs if self._new_step_occurred else 0.0)

    def getLatestGlucoseReading(self) -> float:
        return self._latest_glucose

    def getLatestInsulinIntake(self) -> float:
        return self._latest_insulin if self._new_step_occurred else 0.0

    def getGlucoseData(self) -> List[float]:
        return self._glucose_data

    def getInsulinInjectionData(self) -> List[float]:
        return self._insulin_data

    def getPatientStatus(self) -> str | None:
        # Report status only when a new model step occurred to avoid log spam
        if not self._new_step_occurred:
            return None
        bg = self._latest_glucose
        if bg < HYPO_THRESHOLD:
            return f"Hypoglycemia risk: BG={bg:.1f} mg/dL"
        if bg > HYPER_THRESHOLD:
            return f"Hyperglycemia risk: BG={bg:.1f} mg/dL"
        return None

    # Extra API for UI
    def addCarbIntake(self, grams: float) -> None:
        self._pending_carbs += max(0.0, float(grams))


# ----------------------------
# UI Construction
# ----------------------------
class UIHandles:
    def __init__(self, elements: Dict[str, str], shapes: Dict[str, object]) -> None:
        self.elements = elements
        self.shapes = shapes


def create_ui(patient: Patient, sim_clock: SimulationClock) -> UIHandles:
    elements: Dict[str, str] = {}
    shapes: Dict[str, object] = {}

    with dpg.window(
        label="SIM GLUCOSE",
        height=dpg.get_viewport_max_height(),
        width=dpg.get_viewport_max_width(),
        no_collapse=True,
        no_move=True,
        no_close=True,
        no_title_bar=True,
        tag="root",
    ):
        # Top info panel
        with dpg.child_window(
            label="Sim Info", pos=(20, 20), tag="sim-info", border=True, width=1850, height=120
        ):
            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    with dpg.group():
                        dpg.add_text(
                            default_value="Simulation Controls: ", color=[255, 255, 255, 255], tag="sim-ctrl-txt1"
                        )
                        elements["sim-ctrl-txt1"] = "sim-ctrl-txt1"

                        dpg.add_text(
                            default_value="simulation rate: 1x ", color=[255, 255, 255, 255], tag="sim-rate-txt1"
                        )
                        elements["sim-rate-txt1"] = "sim-rate-txt1"

                        with dpg.group(horizontal=True):
                            dpg.add_button(label="Normal Speed", callback=lambda: sim_clock.setSimulationRate(1))
                            dpg.add_button(label="3X Simulation Speed", callback=lambda: sim_clock.setSimulationRate(3))
                            dpg.add_button(label="6X Simulation Speed", callback=lambda: sim_clock.setSimulationRate(6))
                            dpg.add_spacer(width=8)
                            dpg.add_button(label="Add Carb Intake", callback=open_carb_modal)

                        dpg.add_text(
                            default_value="Time of simulation: 0",
                            tag="sim-time",
                            color=[255, 255, 255, 255],
                        )
                        elements["sim-time"] = "sim-time"

                    with dpg.group():
                        dpg.add_text(default_value="Patient Info: ", color=[255, 255, 255, 255], tag="sim-info-txt1")
                        elements["sim-info-txt1"] = "sim-info-txt1"
                        dpg.add_text(default_value=f"Patient Type: {patient.getPatientType()}")
                        with dpg.group(horizontal=True):
                            dpg.add_text(
                                default_value="Current Glucose Level (mg/dL) 0",
                                tag="sim-pt-glucose",
                                color=[255, 255, 255, 255],
                            )
                            elements["sim-pt-glucose"] = "sim-pt-glucose"

                            dpg.add_text(default_value="", tag="sim-pt-risk", color=[255, 10, 10, 255])
                            elements["sim-pt-risk"] = "sim-pt-risk"

        # Glucose plot
        with dpg.child_window(
            label="Patient Glucose", tag="win", height=250, width=500, pos=(20, 160), border=True, no_scrollbar=True
        ):
            with dpg.plot(
                label="Blood Glucose Levels (ml/dl)",
                height=250,
                width=500,
                no_menus=True,
                no_box_select=True,
                no_mouse_pos=True,
                equal_aspects=False,
            ):
                dpg.add_plot_axis(dpg.mvXAxis, label="Time (seconds)", tag="x_axis")
                elements["x_axis"] = "x_axis"
                dpg.add_plot_axis(dpg.mvYAxis, label="Glucose ml/dl", tag="y_axis")
                elements["y_axis"] = "y_axis"
                dpg.add_line_series([], [], label="Patient Glucose", parent="y_axis", tag="series_tag")
                elements["series_tag"] = "series_tag"

        # Insulin plot
        with dpg.child_window(
            label="Insulin Delivered at timestamp",
            tag="insInj",
            height=250,
            width=500,
            pos=(20, 400),
            border=True,
            no_scrollbar=True,
        ):
            with dpg.plot(
                label="Insulin Dosage injection",
                height=250,
                width=500,
                no_menus=True,
                no_box_select=True,
                no_mouse_pos=True,
                equal_aspects=False,
            ):
                dpg.add_plot_axis(dpg.mvXAxis, label="Time (seconds)", tag="ins-x_axis")
                elements["ins-x_axis"] = "ins-x_axis"
                dpg.add_plot_axis(dpg.mvYAxis, label="Insulin Injection units", tag="ins-y_axis")
                elements["ins-y_axis"] = "ins-y_axis"
                dpg.add_line_series([], [], label="Patient Glucose", parent="ins-y_axis", tag="ins-series_tag")
                elements["ins-series_tag"] = "ins-series_tag"

        # Logs
        with dpg.child_window(label="Patient Logs", tag="logs", width=500, height=250, pos=(20, 670)):
            dpg.add_input_text(
                multiline=True,
                readonly=True,
                width=-1,
                height=-1,
                default_value="Simulation started...\n",
                tag="log_text",
            )
            elements["log_text"] = "log_text"

        # Schematic / devices
        with dpg.child_window(label="Simulation", height=760, width=1320, pos=(550, 160)):
            with dpg.drawlist(height=500, width=920):
                cgm = Circle((250, 250), 50, fillColor=(255, 255, 255, 255), textLabel="CGM")
                mcu = Rectangle(
                    (400, 200), width=150, height=100, textLabel="MCU(ESP-32)\n micro-pump", fillColor=(255, 255, 225, 255)
                )
                ShapeConnection(mcu, cgm)

                phone = PhoneShape((680, 180), width=170, height=200, textLabel="Companion App", fillColor=(255, 255, 255, 255))
                ShapeConnection(phone, mcu)

                shapes["cgm"] = cgm
                shapes["mcu"] = mcu
                shapes["phone"] = phone

    return UIHandles(elements=elements, shapes=shapes)


def _build_carb_modal(patient: Patient) -> None:
    # Hidden modal created at root for reuse
    if dpg.does_item_exist("carb-modal"):
        return
    with dpg.window(label="Carb Intake", modal=True, show=False, tag="carb-modal", no_collapse=True, no_resize=True, width=300, height=150):
        dpg.add_text("Enter carbs (grams):")
        dpg.add_input_float(tag="carb-input", default_value=0.0, min_value=0.0, min_clamped=True, step=1.0, format="%.0f")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Confirm", callback=confirm_carb_intake, user_data=patient)
            dpg.add_button(label="Cancel", callback=cancel_carb_modal)


# ----------------------------
# UI Updates
# ----------------------------
def update_plots_and_labels(ui: UIHandles, sim_clock: SimulationClock, patient: Patient, timestamp: float) -> Tuple[int, int]:
    absolute_time = timestamp + sim_clock._simulationStartTime

    patient.updateGlucoseData(absoluteTimestamp=absolute_time)
    patient.updateInsulinInjectionData(absoluteTimestamp=absolute_time)
    patient.updateCarbIntakeData(absoluteTimestamp=absolute_time)

    bg = int(patient.getLatestGlucoseReading())
    insulin_dose = int(patient.getLatestInsulinIntake())

    dpg.set_value(ui.elements["series_tag"], [sim_clock.getSimulationTimestampData(), patient.getGlucoseData()])
    dpg.fit_axis_data(ui.elements["x_axis"]) 
    dpg.fit_axis_data(ui.elements["y_axis"]) 

    dpg.set_value(ui.elements["ins-series_tag"], [sim_clock.getSimulationTimestampData(), patient.getInsulinInjectionData()])
    dpg.fit_axis_data(ui.elements["ins-x_axis"]) 
    dpg.fit_axis_data(ui.elements["ins-y_axis"]) 

    ddhhmm = seconds_to_ddhhmm(timestamp)
    dpg.set_value(ui.elements["sim-time"], f"Simulation Time: Day: {ddhhmm[0]}, Hour: {ddhhmm[1]}, Minutes: {ddhhmm[2]}")
    dpg.set_value(ui.elements["sim-pt-glucose"], f"Current Glucose Level  {bg} mg/dL")
    dpg.set_value(ui.elements["sim-rate-txt1"], f"simulation rate: {sim_clock.getSimulationRate()}x ")

    risk_color = [255, 0, 0, 255] if bg > HYPER_THRESHOLD or bg < HYPO_THRESHOLD else [0, 255, 0, 255]
    risk_text = "Hyperglycemia" if bg > HYPER_THRESHOLD else ("hypoglycemia " if bg < HYPO_THRESHOLD else "Normal")
    dpg.set_value(ui.elements["sim-pt-risk"], risk_text)
    dpg.configure_item(ui.elements["sim-pt-risk"], color=risk_color)

    return bg, insulin_dose


def apply_visual_state(ui: UIHandles, bg: int, insulin_dose: int) -> None:
    cgm = ui.shapes["cgm"]
    mcu = ui.shapes["mcu"]
    phone = ui.shapes["phone"]

    # BG-based state
    if bg < HYPO_THRESHOLD:
        mcu.updateShapeColor((0, 120, 0, 255))
        phone.updateShapeColor((255, 0, 0, 255))
    elif bg > HYPER_THRESHOLD:
        cgm.updateShapeColor((255, 0, 0, 255))
        phone.updateShapeColor((255, 0, 0, 255))
    else:
        cgm.updateShapeColor((255, 255, 255, 255))
        mcu.updateShapeColor((255, 255, 255, 255))
        phone.updateShapeColor((190, 190, 190, 255))

    # Insulin-based state
    if insulin_dose > 0.1:
        mcu.updateShapeColor((0, 255, 0, 255))
        phone.updateShapeColor((68, 225, 255, 255))
    else:
        t = Timer(interval=2, function=mcu.updateShapeColor, args=((255, 255, 255, 255),))
        t.start()


def maybe_log_patient_state(patient: Patient, timestamp: float) -> None:
    patient_state = patient.getPatientStatus()
    if patient_state:
        d, h, m = seconds_to_ddhhmm(timestamp)
        log_timestamp = f"[D {d}:H {h}:M {m}] : "
        log_msg(log_timestamp + patient_state)


# ----------------------------
# Main Simulation Loop
# ----------------------------
def run_simulation(patient: Patient, sim_clock: SimulationClock) -> None:
    dpg.create_context()
    dpg.create_viewport(title="Glucose Simulation", width=900, height=600)

    ui = create_ui(patient, sim_clock)
    _build_carb_modal(patient)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.maximize_viewport()

    print(sim_clock._simulationStartTime)
    print(
        f"[WAWA] Glucose at sim start time (should be 145 ish) {patient.getGlucoseLevelAtTimestamp(sim_clock._simulationStartTime)}"
    )

    sim_after_8hrs = sim_clock._simulationStartTime + 28800
    print(f"Sim start time + 8 hrs = {sim_after_8hrs}")
    print(f"glucose after 8 hrs = {patient.getGlucoseLevelAtTimestamp(sim_after_8hrs)}")

    sim_clock.setSimulationRate()

    try:
        while dpg.is_dearpygui_running():
            time.sleep(0.02)
            sim_clock.updateClock()

            if keyboard.is_pressed("q"):
                dpg.stop_dearpygui()
                break

            timestamp = sim_clock.getSimulationTime()

            if keyboard.is_pressed("t"):
                ui.shapes["cgm"].updateShapeColor((255, 0, 0, 255))

            bg, insulin_dose = update_plots_and_labels(ui, sim_clock, patient, timestamp)
            apply_visual_state(ui, bg, insulin_dose)
            maybe_log_patient_state(patient, timestamp)

            dpg.render_dearpygui_frame()
    finally:
        dpg.destroy_context()


# ----------------------------
# Entrypoint and Configuration
# ----------------------------
def get_user_config() -> Tuple[bool, int]:
    is_ai_patient = int(input("Enter Patient Type Logic\n1)Ai Patient \n2)Pre simulated\n"))
    if is_ai_patient == 1:
        return True, -1
    patient_type = int(input("Enter Patient Type \n1)child \n2)adolescent \n3)Adult\n"))
    return False, patient_type


def main() -> None:
    use_ai, patient_type = get_user_config()
    if use_ai:
        patient = AiPatientAdapter()
    else:
        patient = Patient(patient_type)

    sim_start_time = patient.getSimStartTime()
    sim_clock = SimulationClock(sim_start_time)
    run_simulation(patient, sim_clock)


if __name__ == "__main__":
    main()


#problem then scope then related work then summarize the then brief overview then ident Gaps