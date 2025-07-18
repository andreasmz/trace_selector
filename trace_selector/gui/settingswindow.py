from PyQt6.QtWidgets import (
    QLabel,
    QFrame,
    QSlider,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSpinBox,
    QCheckBox,
    QLineEdit,
    QDoubleSpinBox,
    QPushButton,
    QComboBox,
    QTabWidget,
    QListWidget,
    QButtonGroup,
    QRadioButton,
    QGridLayout,
)
from PyQt6.QtCore import Qt
import warnings


class SettingsWindow(QWidget):
    def __init__(self, settings, parent, goBackHandler):
        super().__init__()
        self.parent = parent
        self.settings = settings

        self.parse_stim_frames()

        page_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        page_layout.addWidget(self.tab_widget)

        self.setLayout(page_layout)

        self.goBackHandler = goBackHandler

        # --- general ---

        general_layout = QVBoxLayout()

        self.output_folder_path_label = QLabel(
            "Output Folder Path: " + self.settings.config["output_filepath"]
        )
        general_layout.addWidget(self.output_folder_path_label)

        set_path_layout = QHBoxLayout()
        self.button_set_output_path = QPushButton("Set Output Folder Path")
        self.button_set_output_path.clicked.connect(self.set_output_path)
        set_path_layout.addStretch()
        set_path_layout.addWidget(self.button_set_output_path)
        set_path_layout.addStretch()

        self.button_reset_output_path = QPushButton("Reset Output Folder Path")
        self.button_reset_output_path.clicked.connect(self.reset_output_path)
        set_path_layout.addStretch()
        set_path_layout.addWidget(self.button_reset_output_path)
        set_path_layout.addStretch()
        general_layout.addLayout(set_path_layout)

        self.add_line_to_layout(general_layout)

        self.export_normalized_traces = QCheckBox("Export normalized traces")
        self.export_normalized_traces.setToolTip(
            "Absolute traces will be exported as well."
        )
        self.export_normalized_traces.clicked.connect(self.handle_settings_toggle)
        general_layout.addWidget(self.export_normalized_traces)

        self.xlsx_export_box = QCheckBox("Export as .xlsx")
        self.xlsx_export_box.clicked.connect(self.handle_settings_toggle)
        general_layout.addWidget(self.xlsx_export_box)

        column_list_layout = QVBoxLayout()
        column_label = QLabel("Add or remove meta columns for your data:")
        column_list_layout.addWidget(column_label)
        self.column_list = QListWidget(self)
        column_list_layout.addWidget(self.column_list)

        column_input_layout = QHBoxLayout()
        self.input_line_edit = QLineEdit(self)
        column_input_layout.addWidget(self.input_line_edit)
        add_column_button = QPushButton("Add", self)
        add_column_button.clicked.connect(
            lambda: self.add_column_item(self.input_line_edit.text())
        )
        column_input_layout.addWidget(add_column_button)
        remove_column_button = QPushButton("Remove", self)
        remove_column_button.clicked.connect(self.remove_column_item)
        column_input_layout.addWidget(remove_column_button)

        column_list_layout.addLayout(column_input_layout)

        general_layout.addLayout(column_list_layout)

        self.add_line_to_layout(general_layout)

        reset_button_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset Settings")
        self.reset_button.clicked.connect(self.reset_settings)
        reset_button_layout.addStretch()
        reset_button_layout.addWidget(self.reset_button)
        reset_button_layout.addStretch()

        general_layout.addLayout(reset_button_layout)

        general_layout.addStretch()

        general_wrapper_widget = QWidget()
        general_wrapper_widget.setLayout(general_layout)

        # --- response settings ---
        response_layout = QVBoxLayout()

        # peak_detection_type_label = QLabel("Select Detection Method:")
        # response_layout.addWidget(peak_detection_type_label)

        # Renamed to local max detection as it is now not only thresholding. But keep the name thresholding in the code
        self.th_detection_toggle = QCheckBox("Activate Local Maximum Detection")
        self.th_detection_toggle.clicked.connect(self.handle_settings_toggle)
        response_layout.addWidget(self.th_detection_toggle)

        self.ml_detection_toggle = QCheckBox("Activate ML-Based Detection")
        self.ml_detection_toggle.clicked.connect(self.handle_settings_toggle)
        response_layout.addWidget(self.ml_detection_toggle)

        # dropdown_layout = QHBoxLayout()
        # self.peak_detection_type = QComboBox()
        # self.peak_detection_type.addItems(["Thresholding", "ML-based"])
        # self.peak_detection_type.currentIndexChanged.connect(
        #     self.handle_settings_toggle
        # )
        # dropdown_layout.addWidget(self.peak_detection_type)
        # dropdown_layout.addStretch()
        # response_layout.addLayout(dropdown_layout)

        self.ml_model_used = QLabel("Select Deep Learning Model:")
        response_layout.addWidget(self.ml_model_used)

        model_dropdown_layout = QHBoxLayout()
        self.ml_model = QComboBox()
        self.ml_model.addItems(self.settings.modelzoo.available_models.keys())
        self.ml_model.currentIndexChanged.connect(self.handle_settings_toggle)
        model_dropdown_layout.addWidget(self.ml_model)
        model_dropdown_layout.addStretch()
        response_layout.addLayout(model_dropdown_layout)

        self.threshold_label = QLabel("Current Prediction Threshold (ML-based):")
        response_layout.addWidget(self.threshold_label)

        probability_layout = QHBoxLayout()
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.threshold_slider.setMinimumWidth(300)
        self.threshold_slider.setMinimumHeight(40)
        self.threshold_slider.setMinimum(1)
        self.threshold_slider.setMaximum(100)
        self.threshold_slider.setTickInterval(10)
        self.threshold_slider.valueChanged.connect(self.handle_settings_toggle)

        self.current_threshold_label = QLabel(f"{self.threshold_slider.value()}%")

        probability_layout.addWidget(self.threshold_slider)
        probability_layout.addWidget(self.current_threshold_label)
        probability_layout.addStretch()

        response_layout.addLayout(probability_layout)

        self.add_line_to_layout(response_layout)

        tau_desc = QLabel("Time window for tau computation:")
        # tau_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        response_layout.addWidget(tau_desc)

        frames_for_decay_layout = QHBoxLayout()
        self.frames_for_decay = QSpinBox()
        self.frames_for_decay.setToolTip(
            "In the timeframe from peak to the value set, the program will search for the minimum and compute the decay constant tau."
        )
        self.frames_for_decay.valueChanged.connect(self.handle_settings_toggle)
        frames_for_decay_layout.addWidget(self.frames_for_decay)
        frames_for_decay_layout.addStretch()
        response_layout.addLayout(frames_for_decay_layout)

        self.add_line_to_layout(response_layout)

        self.non_max_supression_button = QCheckBox("Use Non-Maximum Supression")
        self.non_max_supression_button.stateChanged.connect(self.handle_settings_toggle)
        response_layout.addWidget(self.non_max_supression_button)

        nms_desc = QLabel("Window for Non-Maximum Supression")
        response_layout.addWidget(nms_desc)

        nms_window_layout = QHBoxLayout()
        self.nms_window = QSpinBox()
        self.nms_window.setToolTip("Window to be used for non-maximum supression")
        self.nms_window.valueChanged.connect(self.handle_settings_toggle)
        nms_window_layout.addWidget(self.nms_window)
        nms_window_layout.addStretch()
        response_layout.addLayout(nms_window_layout)

        self.add_line_to_layout(response_layout)

        # Normalization settings

        self.normalization_grid = QGridLayout()
        response_layout.addLayout(self.normalization_grid)

        self.normalization_grid.addWidget(QLabel("Select a mode for normalization"))
        self.normalization_off = QRadioButton("Do not normalize")
        self.normalization_off.clicked.connect(self.handle_settings_toggle)
        self.normalization_grid.addWidget(self.normalization_off, 1, 0)
        self.normalization_use_mean = QRadioButton("Use mean for normalization")
        self.normalization_use_mean.clicked.connect(self.handle_settings_toggle)
        self.normalization_use_median = QRadioButton("Use median for normalization")
        self.normalization_use_median.clicked.connect(self.handle_settings_toggle)
        self.normalization_grid.addWidget(self.normalization_use_mean, 1, 1)
        self.normalization_grid.addWidget(self.normalization_use_median, 2, 1)
        self.normalization_use_baseline = QRadioButton("Use baseline normalization")
        self.normalization_use_baseline.clicked.connect(self.handle_settings_toggle)
        self.normalization_grid.addWidget(self.normalization_use_baseline, 1, 2)
        self.normalization_group = QButtonGroup(self)
        self.normalization_group.addButton(self.normalization_off, 10)
        self.normalization_group.addButton(self.normalization_use_mean, 11)
        self.normalization_group.addButton(self.normalization_use_median, 12)
        self.normalization_group.addButton(self.normalization_use_baseline, 13)

        normalization_off_layout = QHBoxLayout()
        normalization_median_layout = QHBoxLayout()
        normalization_mean_layout = QHBoxLayout()
        self.normalization_grid.addLayout(normalization_off_layout, 3, 0)
        self.normalization_grid.addLayout(normalization_median_layout, 3, 1)
        self.normalization_grid.addLayout(normalization_mean_layout, 3, 2)

        normalization_off_layout.addStretch()

        normalization_median_layout.addWidget(QLabel("Size of the sliding window:"))
        self.normalization_sliding_window_size = QSpinBox()
        self.normalization_sliding_window_size.setMinimum(2)
        self.normalization_sliding_window_size.setMaximum(200)
        self.normalization_sliding_window_size.valueChanged.connect(self.handle_settings_toggle)
        normalization_median_layout.addWidget(self.normalization_sliding_window_size)
        normalization_median_layout.addStretch()

        normalization_mean_layout.addWidget(QLabel("Start frame:"))
        self.normalization_baseline_start = QSpinBox()
        self.normalization_baseline_start.setMinimum(0)
        self.normalization_baseline_start.setMaximum(10000)
        self.normalization_baseline_start.valueChanged.connect(self.handle_settings_toggle)
        normalization_mean_layout.addWidget(self.normalization_baseline_start)
        normalization_mean_layout.addWidget(QLabel("Length:"))
        self.normalization_baseline_length = QSpinBox()
        self.normalization_baseline_length.setMinimum(1)
        self.normalization_baseline_length.setMaximum(500)
        self.normalization_baseline_length.valueChanged.connect(self.handle_settings_toggle)
        normalization_mean_layout.addWidget(self.normalization_baseline_length)
        normalization_mean_layout.addStretch()

        self.add_line_to_layout(response_layout)

        # Other normalization settings
        

        self.normalized_trace_toggle = QCheckBox("Show normalized trace")
        self.normalized_trace_toggle.clicked.connect(self.handle_settings_toggle)
        response_layout.addWidget(self.normalized_trace_toggle)

        self.activate_response_selection = QCheckBox("Enable response editing")
        self.activate_response_selection.stateChanged.connect(
            self.handle_settings_toggle
        )
        response_layout.addWidget(self.activate_response_selection)

        self.compute_ppr = QCheckBox("Compute PPR")
        self.compute_ppr.stateChanged.connect(self.handle_settings_toggle)
        response_layout.addWidget(self.compute_ppr)

        response_layout.addStretch()

        response_wrapper_widget = QWidget()
        response_wrapper_widget.setLayout(response_layout)

        # --- threshold settings ---

        threshold_layout = QVBoxLayout()

        threshold_layout.addWidget(QLabel("Prominence (A peak is defined as maximum between two valleys of at least prominence)"))
        self.th_prominence_input = QDoubleSpinBox()
        self.th_prominence_input.setMinimumWidth(100)
        self.th_prominence_input.setMinimum(0)
        self.th_prominence_input.setMaximum(1000)
        self.th_prominence_input.setSingleStep(0.01)
        self.th_prominence_input.valueChanged.connect(self.handle_settings_toggle)
        threshold_layout.addWidget(self.th_prominence_input)

        threshold_layout.addWidget(QLabel("Noise multiplier (Noise is estimated to be mean + std*noise_multiplier)"))
        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setMinimumWidth(100)
        self.threshold_input.setMinimum(0)
        self.threshold_input.setMaximum(100)
        self.threshold_input.setSingleStep(0.05)
        self.threshold_input.valueChanged.connect(self.handle_settings_toggle)
        threshold_layout.addWidget(self.threshold_input)

        self.show_threshold = QCheckBox("Display estimated noise")
        self.show_threshold.stateChanged.connect(self.handle_settings_toggle)
        threshold_layout.addWidget(self.show_threshold)

        threshold_layout.addWidget(QLabel("Minimum peak distance"))
        self.th_mindistance_input = QSpinBox()
        self.th_mindistance_input.setMinimumWidth(100)
        self.th_mindistance_input.setMinimum(0)
        self.th_mindistance_input.setMaximum(1000)
        self.th_mindistance_input.valueChanged.connect(self.handle_settings_toggle)
        threshold_layout.addWidget(self.th_mindistance_input)

        self.threshold_wrapper_widget = QWidget()
        self.threshold_wrapper_widget.setLayout(threshold_layout)

        th_frame_subset_layout = QHBoxLayout()
        threshold_layout.addLayout(th_frame_subset_layout)

        self.th_use_frame_subset = QCheckBox("Use a subset to calculate the baseline")
        self.th_use_frame_subset.stateChanged.connect(self.handle_settings_toggle)
        th_frame_subset_layout.addWidget(self.th_use_frame_subset)

        th_frame_subset_layout.addWidget(QLabel("Start frame:"))
        self.th_subset_start = QSpinBox()
        self.th_subset_start.setMinimum(0)
        self.th_subset_start.setMaximum(10000)
        self.th_subset_start.valueChanged.connect(self.handle_settings_toggle)
        th_frame_subset_layout.addWidget(self.th_subset_start)
        th_frame_subset_layout.addWidget(QLabel("Length:"))
        self.th_subset_length = QSpinBox()
        self.th_subset_length.setMinimum(1)
        self.th_subset_length.setMaximum(500)
        self.th_subset_length.valueChanged.connect(self.handle_settings_toggle)
        th_frame_subset_layout.addWidget(self.th_subset_length)
        th_frame_subset_layout.addStretch()

        threshold_layout.addStretch()



        # --- stimulation settings ---

        stimulation_layout = QVBoxLayout()

        self.stim_used_box = QCheckBox("Enable Stimulation")
        self.stim_used_box.stateChanged.connect(self.handle_settings_toggle)
        stimulation_layout.addWidget(self.stim_used_box)

        self.start_stimulation_label = QLabel("Startframe for Stimulation")
        stimulation_layout.addWidget(self.start_stimulation_label)

        start_simulation_layout = QHBoxLayout()
        self.start_stimulation_input = QSpinBox()
        self.start_stimulation_input.setMinimumWidth(100)
        self.start_stimulation_input.setMaximum(100_000)
        self.start_stimulation_input.editingFinished.connect(
            self.handle_settings_toggle
        )
        start_simulation_layout.addWidget(self.start_stimulation_input)
        start_simulation_layout.addStretch()
        stimulation_layout.addLayout(start_simulation_layout)

        self.step_stimulation_label = QLabel("Step Size for Stimulation")
        stimulation_layout.addWidget(self.step_stimulation_label)

        step_simulation_layout = QHBoxLayout()
        self.step_stimulation_input = QSpinBox()
        self.step_stimulation_input.setMinimumWidth(100)
        self.step_stimulation_input.setMaximum(100_000)
        self.step_stimulation_input.editingFinished.connect(self.handle_settings_toggle)
        step_simulation_layout.addWidget(self.step_stimulation_input)
        step_simulation_layout.addStretch()
        stimulation_layout.addLayout(step_simulation_layout)

        self.patience_label = QLabel("Patience")
        self.patience_label.setMinimumWidth(100)
        stimulation_layout.addWidget(self.patience_label)

        patience_input_layout = QHBoxLayout()
        self.patience_input_l = QSpinBox()
        self.patience_input_l.setMinimum(0)
        self.patience_input_l.setMaximum(100)
        self.patience_input_l.editingFinished.connect(self.handle_settings_toggle)
        self.patience_input_r = QSpinBox()
        self.patience_input_r.setMinimum(0)
        self.patience_input_r.setMaximum(100)
        self.patience_input_r.editingFinished.connect(self.handle_settings_toggle)
        patience_input_layout.addWidget(QLabel("Left"))
        patience_input_layout.addWidget(self.patience_input_l)
        patience_input_layout.addWidget(QLabel("Right"))
        patience_input_layout.addWidget(self.patience_input_r)
        patience_input_layout.addStretch()
        stimulation_layout.addLayout(patience_input_layout)

        self.add_line_to_layout(stimulation_layout)

        self.manual_stim_frames = QCheckBox("Use manual stim frames")
        self.manual_stim_frames.stateChanged.connect(self.handle_settings_toggle)
        stimulation_layout.addWidget(self.manual_stim_frames)

        self.stimframes_label = QLabel("Manual Input of Stimulation Frames")
        stimulation_layout.addWidget(self.stimframes_label)

        stimframes_input_layout = QHBoxLayout()
        self.stimframes_input = QLineEdit()
        self.stimframes_input.editingFinished.connect(self.handle_settings_toggle)
        stimframes_input_layout.addWidget(self.stimframes_input)
        stimframes_input_layout.addStretch()
        stimulation_layout.addLayout(stimframes_input_layout)

        stimulation_layout.addStretch()

        stimulation_wrapper_widget = QWidget()
        stimulation_wrapper_widget.setLayout(stimulation_layout)

        # --- buttons ---

        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.handle_save_button)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.handle_cancel_button)

        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()

        page_layout.addLayout(button_layout)

        self.tab_widget.addTab(general_wrapper_widget, "General")
        self.tab_widget.addTab(response_wrapper_widget, "Detection")
        self.tab_widget.addTab(self.threshold_wrapper_widget, "Local Maximum Detection Settings")
        self.tab_widget.addTab(stimulation_wrapper_widget, "Stimulation")

        self.initialize_widget_values()

    def reset_settings(self):
        self.settings.remove_user_settings()
        self.settings.parse_settings()
        self.initialize_widget_values()

    def add_column_item(self, new_column):
        if new_column:
            self.column_list.addItem(new_column)
            self.input_line_edit.clear()

    def remove_column_item(self):
        current_row = self.column_list.currentRow()
        if current_row >= 0:
            self.column_list.takeItem(current_row)

    def initialize_widget_values(self):
        self.patience_input_l.setValue(self.settings.config["stim_frames_patience_l"])
        self.patience_input_r.setValue(self.settings.config["stim_frames_patience_r"])
        self.stimframes_input.setText(self.settings.config["stim_frames"])
        self.stim_used_box.setChecked(self.settings.config["stim_used"])
        self.xlsx_export_box.setChecked(self.settings.config["export_xlsx"])
        self.export_normalized_traces.setChecked(
            self.settings.config["export_normalized_traces"]
        )

        # Normalization settings
        _selected_button = self.normalization_group.button(int(self.settings.config["normalization_mode"]))
        if _selected_button is None:
            _selected_button = self.normalization_use_median
        _selected_button.setChecked(True)

        self.normalization_sliding_window_size.setValue(self.settings.config["normalization_sliding_window_size"])

        baseline_norm_window = self.settings.config["normalization_baseline_window"].split(":")
        if len(baseline_norm_window) != 2: baseline_norm_window = ["-1", "-1"]
        baseline_norm_start = int(baseline_norm_window[0])
        baseline_norm_length = int(baseline_norm_window[1]) - baseline_norm_start
        self.normalization_baseline_start.setValue(baseline_norm_start)
        self.normalization_baseline_length.setValue(baseline_norm_length)

        # Detection settings

        #  Local maximum settings
        self.th_prominence_input.setValue(self.settings.config["threshold_prominence"])
        self.threshold_input.setValue(self.settings.config["threshold_mult"])
        self.th_mindistance_input.setValue(self.settings.config["threshold_mindistance"])
        self.show_threshold.setChecked(self.settings.config["always_show_threshold"])
        self.th_use_frame_subset.setChecked(self.settings.config["th_use_frame_subset"])
        self.th_subset_start.setValue(self.settings.config["th_subset_start"])
        self.th_subset_length.setValue(self.settings.config["th_subset_length"])

        self.ml_detection_toggle.setChecked(self.settings.config["ml_detection"])
        self.th_detection_toggle.setChecked(self.settings.config["th_detection"])
        self.ml_model.setCurrentIndex(0)
        self.threshold_slider.setValue(self.settings.config["threshold_slider_ml"])
        self.frames_for_decay.setValue(self.settings.config["frames_for_decay"])
        self.normalized_trace_toggle.setChecked(
            self.settings.config["normalized_trace"]
        )
        self.activate_response_selection.setChecked(
            self.settings.config["select_responses"]
        )
        self.non_max_supression_button.setChecked(self.settings.config["nms"])
        self.nms_window.setValue(self.settings.config["nms_window"])
        self.use_nms = self.settings.config["nms"]
        self.compute_ppr.setChecked(self.settings.config["compute_ppr"])
        self.start_stimulation_input.setValue(self.settings.config["stim_frames_start"])
        self.step_stimulation_input.setValue(self.settings.config["stim_frames_step"])
        self.manual_stim_frames.setChecked(
            self.settings.config["use_manual_stim_frames"]
        )

        # remove all meta columns to reset list widget
        self.column_list.clear()
        # add existing meta columns
        for column in self.settings.config["meta_columns"]:
            self.add_column_item(column)

    def handle_save_button(self):
        self.update_settings()
        self.goBackHandler()

    def handle_cancel_button(self):
        self.settings.parse_settings()
        self.initialize_widget_values()
        self.goBackHandler()

    def reset_output_path(self):
        self.settings.config["output_filepath"] = ""
        self.update_settings()
        self.update_output_path("")

    def add_line_to_layout(self, layout):
        # Add a horizontal line
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

    def set_output_path(self):
        self.settings.get_output_folder(self)
        self.update_settings()
        self.update_output_path(self.settings.config["output_filepath"])

    def update_output_path(self, path: str):
        self.output_folder_path_label.setText("Output Folder Path: " + path)

    def update_settings(self) -> None:
        """
        Whenever any setting is changed this function is called and notes that
        change in the settings_.config dictionary, that is used internally to
        provide the user set configurations.
        """
        # update all values that might have been changed

        # Local maximum settings
        self.settings.config["threshold_prominence"] = self.th_prominence_input.value()
        self.settings.config["threshold_mult"] = self.threshold_input.value()
        self.settings.config["threshold_mindistance"] = self.th_mindistance_input.value()
        self.settings.config["always_show_threshold"] = self.show_threshold.isChecked()
        self.settings.config["th_use_frame_subset"] = self.th_use_frame_subset.isChecked()
        self.settings.config["th_subset_start"] = self.th_subset_start.value()
        self.settings.config["th_subset_length"] = self.th_subset_length.value()

        self.th_use_frame_subset.setChecked(self.settings.config["th_use_frame_subset"])
        self.th_subset_start.setValue(self.settings.config["th_subset_start"])
        self.th_subset_length.setValue(self.settings.config["th_subset_length"])


        self.settings.config["stim_frames_patience_l"] = self.patience_input_l.value()
        self.settings.config["stim_frames_patience_r"] = self.patience_input_r.value()
        self.settings.config["frames_for_decay"] = self.frames_for_decay.value()
        self.settings.config["stim_frames"] = self.stimframes_input.text()
        self.settings.config["th_detection"] = self.th_detection_toggle.isChecked()
        self.settings.config["ml_detection"] = self.ml_detection_toggle.isChecked()
        model_path = self.settings.modelzoo.available_models[
            self.ml_model.currentText()
        ]["filepath"]
        self.settings.config["model_path"] = model_path
        self.settings.config["nms"] = self.non_max_supression_button.isChecked()
        self.settings.config["nms_window"] = self.nms_window.value()
        self.settings.config["stim_used"] = self.stim_used_box.isChecked()
        self.settings.config[
            "select_responses"
        ] = self.activate_response_selection.isChecked()
        self.settings.config["compute_ppr"] = self.compute_ppr.isChecked()
        self.settings.config[
            "export_normalized_traces"
        ] = self.export_normalized_traces.isChecked()
        self.settings.config["export_xlsx"] = self.xlsx_export_box.isChecked()

        # Normalization settings
        self.settings.config["normalization_mode"] = self.normalization_group.checkedId()
        self.settings.config["normalization_sliding_window_size"] = self.normalization_sliding_window_size.value()
        self.settings.config[
            "normalization_baseline_window"
        ] = "%i:%i" % (self.normalization_baseline_start.value(), self.normalization_baseline_start.value()+self.normalization_baseline_length.value())


        self.settings.config[
            "normalized_trace"
        ] = self.normalized_trace_toggle.isChecked()
        self.settings.config["threshold_slider_ml"] = self.threshold_slider.value()
        self.settings.config["stim_frames_start"] = self.start_stimulation_input.value()
        self.settings.config["stim_frames_step"] = self.step_stimulation_input.value()
        self.settings.config[
            "use_manual_stim_frames"
        ] = self.manual_stim_frames.isChecked()

        new_meta_columns = []
        for index in range(self.column_list.count()):
            item = self.column_list.item(index)
            if item is not None:
                new_meta_columns.append(item.text())

        self.settings.config["meta_columns"] = new_meta_columns

        self.parse_stim_frames()
        self.handle_settings_toggle()
        self.check_patience()

        if (
            self.settings.config["ml_detection"]
            and not self.settings.config["th_detection"]
            and self.settings.config["model_path"] == ""
        ):
            warnings.warn("No model selected. Will activate thresholding")
            self.settings.config["th_detection"] = True

        # update settings
        self.parent.settings = self.settings
        self.settings.write_settings()
        self.parent.stimframes = self.stimframes

        # replot whenever any setting is changed
        if self.parent.synapse_response.file_opened:
            self.parent.plot(new_sample=False)

        # update threshold slider in main window
        self.parent.refresh_slider()

    def parse_stim_frames(self):
        if len(self.settings.config["stim_frames"]) > 0:
            self.stimframes = [
                int(frame) for frame in self.settings.config["stim_frames"].split(",")
            ]
            self.stimframes = sorted(self.stimframes)
        else:
            self.stimframes = []

    def check_patience(self) -> None:
        self.patience_input_l.setStyleSheet("")
        self.patience_input_r.setStyleSheet("")
        if not self.compute_ppr.isChecked() or len(self.stimframes) <= 1:
            return
        min_distance = self.stimframes[1] - self.stimframes[0]
        for i in range(len(self.stimframes) - 1):
            if self.stimframes[i + 1] - self.stimframes[i] < min_distance:
                min_distance = self.stimframes[i + 1] - self.stimframes[i]
        if min_distance < (self.settings.config["stim_frames_patience_l"] + self.settings.config["stim_frames_patience_r"]):
            self.patience_input_l.setStyleSheet(
                "QSpinBox" "{" "background : #ff5959;" "}"
            )
            self.patience_input_r.setStyleSheet(
                "QSpinBox" "{" "background : #ff5959;" "}"
            )

    def handle_settings_toggle(self) -> None:
        self.current_threshold_label.setText(f"{self.threshold_slider.value()}%")

        if self.ml_detection_toggle.isChecked():
            self.ml_model.setEnabled(True)
            self.ml_model_used.setEnabled(True)
            self.threshold_label.setEnabled(True)
            self.current_threshold_label.setEnabled(True)
            self.threshold_slider.setEnabled(True)
        else:
            self.ml_model.setEnabled(False)
            self.ml_model_used.setEnabled(False)
            self.threshold_label.setEnabled(False)
            self.current_threshold_label.setEnabled(False)
            self.threshold_slider.setEnabled(False)

        if self.stim_used_box.isChecked():
            self.stimframes_input.setEnabled(True)
            self.stimframes_label.setEnabled(True)
            self.compute_ppr.setEnabled(True)
            self.patience_label.setEnabled(True)
            self.patience_input_l.setEnabled(True)
            self.patience_input_r.setEnabled(True)
        else:
            self.stimframes_input.setEnabled(False)
            self.stimframes_label.setEnabled(False)
            self.patience_label.setEnabled(False)
            self.patience_input_l.setEnabled(False)
            self.patience_input_r.setEnabled(False)
            self.compute_ppr.setEnabled(False)

        if self.non_max_supression_button.isChecked():
            self.nms_window.setEnabled(True)
        else:
            self.nms_window.setEnabled(False)

        # activate add response button depending on setting
        if self.activate_response_selection.isChecked():
            self.parent.button_add.setEnabled(True)
            self.compute_ppr.setEnabled(True)
            self.non_max_supression_button.setEnabled(True)
        else:
            self.parent.button_add.setDisabled(True)
            self.compute_ppr.setEnabled(False)
            self.non_max_supression_button.setEnabled(False)

    # this is being called by the parent to synchronise the threshold slider value
    def update_ml_slider_value(self, value) -> None:
        self.settings.config["threshold_slider_ml"] = value
        self.threshold_slider.setValue(value)
        self.update_settings()