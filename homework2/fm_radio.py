#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: FM Radio
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
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, GrRangeWidget
from PyQt5 import QtCore
import fm_radio_freq_module as freq_module  # embedded python module
import osmosdr
import time



from gnuradio import qtgui

class fm_radio(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "FM Radio", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("FM Radio")
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

        self.settings = Qt.QSettings("GNU Radio", "fm_radio")

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
        self.station_chooser = station_chooser = 90.3e6
        self.samp_rate = samp_rate = 5e6
        self.freq_change = freq_change = 88.5e6
        self.channel_width = channel_width = 200e3
        self.browse = browse = True

        ##################################################
        # Blocks
        ##################################################
        # Create the options list
        self._station_chooser_options = [90300000.0, 94400000.0, 99400000.0, 100200000.0, 104200000.0]
        # Create the labels list
        self._station_chooser_labels = ['90.3', '94.4', '99.4', '100.2', '104.2']
        # Create the combo box
        self._station_chooser_tool_bar = Qt.QToolBar(self)
        self._station_chooser_tool_bar.addWidget(Qt.QLabel("Select saved station" + ": "))
        self._station_chooser_combo_box = Qt.QComboBox()
        self._station_chooser_tool_bar.addWidget(self._station_chooser_combo_box)
        for _label in self._station_chooser_labels: self._station_chooser_combo_box.addItem(_label)
        self._station_chooser_callback = lambda i: Qt.QMetaObject.invokeMethod(self._station_chooser_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._station_chooser_options.index(i)))
        self._station_chooser_callback(self.station_chooser)
        self._station_chooser_combo_box.currentIndexChanged.connect(
            lambda i: self.set_station_chooser(self._station_chooser_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._station_chooser_tool_bar, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._freq_change_range = Range(88e6, 108e6, 1e5, 88.5e6, 200)
        self._freq_change_win = GrRangeWidget(self._freq_change_range, self.set_freq_change, "Choose frequency", "counter_slider", float, QtCore.Qt.Horizontal, "value")

        self.top_grid_layout.addWidget(self._freq_change_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        _browse_check_box = Qt.QCheckBox("Browse")
        self._browse_choices = {True: True, False: False}
        self._browse_choices_inv = dict((v,k) for k,v in self._browse_choices.items())
        self._browse_callback = lambda i: Qt.QMetaObject.invokeMethod(_browse_check_box, "setChecked", Qt.Q_ARG("bool", self._browse_choices_inv[i]))
        self._browse_callback(self.browse)
        _browse_check_box.stateChanged.connect(lambda i: self.set_browse(self._browse_choices[bool(i)]))
        self.top_grid_layout.addWidget(_browse_check_box, 4, 0, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=12,
                decimation=5,
                taps=[],
                fractional_bw=0)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq_module.set_center_frequency(freq_change) if browse == 1 else freq_module.set_center_frequency(station_chooser) , #fc
            samp_rate, #bw
            "Original Input", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.1)
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

        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq_change if browse == 1 else station_chooser, #fc
            samp_rate, #bw
            "Adjusted Signals", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.osmosdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(freq_module.set_center_frequency(freq_change) if browse == 1 else freq_module.set_center_frequency(station_chooser) , 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(10, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            25,
            firdes.low_pass(
                1,
                samp_rate,
                (int(0.75*(channel_width/2))),
                (int(0.25*(channel_width/2))),
                window.WIN_HAMMING,
                6.76))
        self.dc_blocker_xx_0 = filter.dc_blocker_cc(1024, True)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.audio_sink_0 = audio.sink(48000, '', True)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=480e3,
        	audio_decimation=10,
        )
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, (freq_module.set_center_frequency(freq_change) - freq_change if browse == 1 else freq_module.set_center_frequency(station_chooser) - station_chooser), 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_wfm_rcv_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.dc_blocker_xx_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.dc_blocker_xx_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_wfm_rcv_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "fm_radio")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_station_chooser(self):
        return self.station_chooser

    def set_station_chooser(self, station_chooser):
        self.station_chooser = station_chooser
        self._station_chooser_callback(self.station_chooser)
        self.analog_sig_source_x_0.set_frequency((freq_module.set_center_frequency(self.freq_change) - self.freq_change if self.browse == 1 else freq_module.set_center_frequency(self.station_chooser) - self.station_chooser))
        self.osmosdr_source_0.set_center_freq(freq_module.set_center_frequency(self.freq_change) if self.browse == 1 else freq_module.set_center_frequency(self.station_chooser) , 0)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_change if self.browse == 1 else self.station_chooser, self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(freq_module.set_center_frequency(self.freq_change) if self.browse == 1 else freq_module.set_center_frequency(self.station_chooser) , self.samp_rate)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, (int(0.75*(self.channel_width/2))), (int(0.25*(self.channel_width/2))), window.WIN_HAMMING, 6.76))
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_change if self.browse == 1 else self.station_chooser, self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(freq_module.set_center_frequency(self.freq_change) if self.browse == 1 else freq_module.set_center_frequency(self.station_chooser) , self.samp_rate)

    def get_freq_change(self):
        return self.freq_change

    def set_freq_change(self, freq_change):
        self.freq_change = freq_change
        self.analog_sig_source_x_0.set_frequency((freq_module.set_center_frequency(self.freq_change) - self.freq_change if self.browse == 1 else freq_module.set_center_frequency(self.station_chooser) - self.station_chooser))
        self.osmosdr_source_0.set_center_freq(freq_module.set_center_frequency(self.freq_change) if self.browse == 1 else freq_module.set_center_frequency(self.station_chooser) , 0)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_change if self.browse == 1 else self.station_chooser, self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(freq_module.set_center_frequency(self.freq_change) if self.browse == 1 else freq_module.set_center_frequency(self.station_chooser) , self.samp_rate)

    def get_channel_width(self):
        return self.channel_width

    def set_channel_width(self, channel_width):
        self.channel_width = channel_width
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, (int(0.75*(self.channel_width/2))), (int(0.25*(self.channel_width/2))), window.WIN_HAMMING, 6.76))

    def get_browse(self):
        return self.browse

    def set_browse(self, browse):
        self.browse = browse
        self._browse_callback(self.browse)
        self.analog_sig_source_x_0.set_frequency((freq_module.set_center_frequency(self.freq_change) - self.freq_change if self.browse == 1 else freq_module.set_center_frequency(self.station_chooser) - self.station_chooser))
        self.osmosdr_source_0.set_center_freq(freq_module.set_center_frequency(self.freq_change) if self.browse == 1 else freq_module.set_center_frequency(self.station_chooser) , 0)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_change if self.browse == 1 else self.station_chooser, self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(freq_module.set_center_frequency(self.freq_change) if self.browse == 1 else freq_module.set_center_frequency(self.station_chooser) , self.samp_rate)




def main(top_block_cls=fm_radio, options=None):

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
