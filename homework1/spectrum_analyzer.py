#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Analyzer
# Author: Nikita Filin
# GNU Radio version: 3.10.4.0

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import eng_notation
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio.qtgui import Range, GrRangeWidget
from PyQt5 import QtCore
import osmosdr
import time



from gnuradio import qtgui

class spectrum_analyzer(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Analyzer", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Analyzer")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "spectrum_analyzer")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 5e6
        self.predefined_options = predefined_options = 9.8e7
        self.options_label = options_label = 'Range Selector:'
        self.mode_chooser = mode_chooser = 0
        self.freq_change = freq_change = 24e8
        self.browse_by_label = browse_by_label = 'Browse by:'

        ##################################################
        # Blocks
        ##################################################
        # Create the options list
        self._predefined_options_options = [98000000.0, 2400000000.0, 868000000.0, 1227000000.0]
        # Create the labels list
        self._predefined_options_labels = ['FM Radio', 'WiFi', 'ISM', 'GPS']
        # Create the combo box
        # Create the radio buttons
        self._predefined_options_group_box = Qt.QGroupBox("'predefined_options'" + ": ")
        self._predefined_options_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._predefined_options_button_group = variable_chooser_button_group()
        self._predefined_options_group_box.setLayout(self._predefined_options_box)
        for i, _label in enumerate(self._predefined_options_labels):
            radio_button = Qt.QRadioButton(_label)
            self._predefined_options_box.addWidget(radio_button)
            self._predefined_options_button_group.addButton(radio_button, i)
        self._predefined_options_callback = lambda i: Qt.QMetaObject.invokeMethod(self._predefined_options_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._predefined_options_options.index(i)))
        self._predefined_options_callback(self.predefined_options)
        self._predefined_options_button_group.buttonClicked[int].connect(
            lambda i: self.set_predefined_options(self._predefined_options_options[i]))
        self.top_grid_layout.addWidget(self._predefined_options_group_box, 4, 0, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._mode_chooser_options = [0, 1]
        # Create the labels list
        self._mode_chooser_labels = ['Slider', 'Quick select']
        # Create the combo box
        # Create the radio buttons
        self._mode_chooser_group_box = Qt.QGroupBox("'mode_chooser'" + ": ")
        self._mode_chooser_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._mode_chooser_button_group = variable_chooser_button_group()
        self._mode_chooser_group_box.setLayout(self._mode_chooser_box)
        for i, _label in enumerate(self._mode_chooser_labels):
            radio_button = Qt.QRadioButton(_label)
            self._mode_chooser_box.addWidget(radio_button)
            self._mode_chooser_button_group.addButton(radio_button, i)
        self._mode_chooser_callback = lambda i: Qt.QMetaObject.invokeMethod(self._mode_chooser_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._mode_chooser_options.index(i)))
        self._mode_chooser_callback(self.mode_chooser)
        self._mode_chooser_button_group.buttonClicked[int].connect(
            lambda i: self.set_mode_chooser(self._mode_chooser_options[i]))
        self.top_grid_layout.addWidget(self._mode_chooser_group_box, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._freq_change_range = Range(1e6, 6e9, 0.1e6, 24e8, 200)
        self._freq_change_win = GrRangeWidget(self._freq_change_range, self.set_freq_change, "Frequency slider", "counter_slider", float, QtCore.Qt.Horizontal, "value")

        self.top_grid_layout.addWidget(self._freq_change_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq_change if mode_chooser == 0 else predefined_options, #fc
            samp_rate, #bw
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.qwidget(), Qt.QWidget)

        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win, 5, 0, 1, 1)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq_change if mode_chooser == 0 else predefined_options, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(2)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 6, 0, 1, 1)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq_change if mode_chooser == 0 else predefined_options, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(10, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
        self._options_label_tool_bar = Qt.QToolBar(self)

        if None:
            self._options_label_formatter = None
        else:
            self._options_label_formatter = lambda x: str(x)

        self._options_label_tool_bar.addWidget(Qt.QLabel(" "))
        self._options_label_label = Qt.QLabel(str(self._options_label_formatter(self.options_label)))
        self._options_label_tool_bar.addWidget(self._options_label_label)
        self.top_grid_layout.addWidget(self._options_label_tool_bar, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._browse_by_label_tool_bar = Qt.QToolBar(self)

        if None:
            self._browse_by_label_formatter = None
        else:
            self._browse_by_label_formatter = lambda x: str(x)

        self._browse_by_label_tool_bar.addWidget(Qt.QLabel(" "))
        self._browse_by_label_label = Qt.QLabel(str(self._browse_by_label_formatter(self.browse_by_label)))
        self._browse_by_label_tool_bar.addWidget(self._browse_by_label_label)
        self.top_grid_layout.addWidget(self._browse_by_label_tool_bar, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_throttle_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_throttle_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "spectrum_analyzer")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_change if self.mode_chooser == 0 else self.predefined_options, self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.freq_change if self.mode_chooser == 0 else self.predefined_options, self.samp_rate)

    def get_predefined_options(self):
        return self.predefined_options

    def set_predefined_options(self, predefined_options):
        self.predefined_options = predefined_options
        self._predefined_options_callback(self.predefined_options)
        self.osmosdr_source_0.set_center_freq(self.freq_change if self.mode_chooser == 0 else self.predefined_options, 0)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_change if self.mode_chooser == 0 else self.predefined_options, self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.freq_change if self.mode_chooser == 0 else self.predefined_options, self.samp_rate)

    def get_options_label(self):
        return self.options_label

    def set_options_label(self, options_label):
        self.options_label = options_label
        Qt.QMetaObject.invokeMethod(self._options_label_label, "setText", Qt.Q_ARG("QString", str(self._options_label_formatter(self.options_label))))

    def get_mode_chooser(self):
        return self.mode_chooser

    def set_mode_chooser(self, mode_chooser):
        self.mode_chooser = mode_chooser
        self._mode_chooser_callback(self.mode_chooser)
        self.osmosdr_source_0.set_center_freq(self.freq_change if self.mode_chooser == 0 else self.predefined_options, 0)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_change if self.mode_chooser == 0 else self.predefined_options, self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.freq_change if self.mode_chooser == 0 else self.predefined_options, self.samp_rate)

    def get_freq_change(self):
        return self.freq_change

    def set_freq_change(self, freq_change):
        self.freq_change = freq_change
        self.osmosdr_source_0.set_center_freq(self.freq_change if self.mode_chooser == 0 else self.predefined_options, 0)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_change if self.mode_chooser == 0 else self.predefined_options, self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.freq_change if self.mode_chooser == 0 else self.predefined_options, self.samp_rate)

    def get_browse_by_label(self):
        return self.browse_by_label

    def set_browse_by_label(self, browse_by_label):
        self.browse_by_label = browse_by_label
        Qt.QMetaObject.invokeMethod(self._browse_by_label_label, "setText", Qt.Q_ARG("QString", str(self._browse_by_label_formatter(self.browse_by_label))))




def main(top_block_cls=spectrum_analyzer, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
