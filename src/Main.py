from cProfile import label

from matplotlib.pyplot import xlabel
from gui import Ui_MainWindow
import os
import numpy as np
import math
from scipy.fftpack import fft, fftfreq
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog


class IllustratorGUI(Ui_MainWindow):
    def show_secondary_graph(self):
        if self.menuHide.title() == "hide":
            self.secondaryGraph.setVisible(False)
            self.secondryGraph_label.setVisible(False)
            self.secondryGraph_info.setVisible(False)
            self.menuHide.setTitle("show")

        else:
            self.secondaryGraph.setVisible(True)
            self.secondryGraph_label.setVisible(True)
            self.secondryGraph_info.setVisible(True)
            self.menuHide.setTitle("hide")

    def setupUi(self, MainWindow):
        Ui_MainWindow.setupUi(self, MainWindow)
        self.show_secondary_graph()


class IllustratorApplication(QtWidgets.QMainWindow):
    exported_signal_index = "resultant_signal_from_composer"
    interpolate_f = 0
    def __init__(self):
        super(IllustratorApplication, self).__init__()
        self.gui = IllustratorGUI()
        self.gui.setupUi(self)
        self.sinusoidal = None
        self.Signal_test = None
        self.Dotted_plot = None
        self.index1=0
        self.index2=0

        self.set_widget_function()

    def set_widget_function(self):
        # Buttons
        self.gui.actionSignals.triggered.connect(self.open_sig_file)
        self.gui.show_sin_Button.clicked.connect(self.plot_sig_on_composerGraph)
        self.gui.add_sin_Button.clicked.connect(self.add_sig_to_resultantGraph)
        self.gui.sinusoidal_list_comboBox.activated.connect(self.plot_sigComponent)
        self.gui.delete_sin_Button.clicked.connect(self.delete_sigComponent_from_resultantGraph)
        self.gui.confirm_sig_Button.clicked.connect(self.plot_resultant_sig_on_mainGraph)
        # slider:
        self.gui.samplingFreq_Slider.valueChanged.connect(
            lambda: self.Renew_Intr(self.gui.samplingFreq_Slider.value()))
        self.gui.actionSecondary_Graph_hide.triggered.connect(self.gui.show_secondary_graph)

    def open_sig_file(self):
        try:
            files_name = QFileDialog.getOpenFileName(self, 'Open only txt or CSV or xls', os.getenv('HOME'),
                                                     "(*.csv *.txt *.xls)")
            path = files_name[0]
            Signal_Name = path.split('/')[-1].split(".")[0]
            data = np.genfromtxt(path, delimiter=',')
            time = list(data[1:, 0])
            y_axis = list(data[1:, 1])
            self.plotOnMain(time[0:1000], y_axis[0:1000], Signal_Name)
        except:
            pass

    def plot_sig_on_composerGraph(self):
        if self.gui.show_sin_Button.text()=="Show":
            self.gui.composerGraph.clear()
            name = self.gui.name_lineEdit.text()
            freq = self.gui.frequency_lineEdit.text()
            amp = self.gui.amplitude_lineEdit.text()
            phase = self.gui.phase_lineEdit.text()
            if name in storage.componentSin.keys():
                name+=str(self.index1)
                self.index1+=1
            elif name == "":
                name = "standard name"+str(self.index2)
                self.index2+=1

            freq = IllustratorApplication.return_zero_at_emptyString(freq)
            amp = IllustratorApplication.return_zero_at_emptyString(amp)
            phase = IllustratorApplication.return_zero_at_emptyString(phase)
            self.sinusoidal = Sinusoidals(name, float(freq), float(amp), float(phase))
            self.gui.composerGraph.plot(self.sinusoidal.time, self.sinusoidal.y_axis_value, pen='r')

            self.gui.show_sin_Button.setText("Delete")
        else:    
            self.gui.composerGraph.clear()
            self.clear_lineedit()
            self.gui.show_sin_Button.setText("Show")
            self.sinusoidal=None


    def clear_lineedit(self):
        self.gui.name_lineEdit.clear()
        self.gui.frequency_lineEdit.clear()
        self.gui.amplitude_lineEdit.clear()
        self.gui.phase_lineEdit.clear()
    
    def add_sig_to_resultantGraph(self):
        # add try except statement
        if self.sinusoidal != None:
            self.gui.sinusoidal_list_comboBox.addItem(self.sinusoidal.name)
            self.gui.resultant_signalGraph.clear()
            storage.componentSin[self.sinusoidal.name] = self.sinusoidal
            self.sinusoidal.add_sig_to_result()
            self.gui.resultant_signalGraph.plot(Sinusoidals.resultant_sig[0], Sinusoidals.resultant_sig[1], pen='r',
                                        )
            self.sinusoidal = None
            self.gui.composerGraph.clear()
            self.gui.show_sin_Button.setText("Show")
            self.clear_lineedit()

 
    def plot_sigComponent(self):
        self.gui.composerGraph.clear()
        signal_component = storage.componentSin[self.gui.sinusoidal_list_comboBox.currentText()]
        self.gui.composerGraph.plot(signal_component.time, signal_component.y_axis_value, pen='r',
                                   )

    def delete_sigComponent_from_resultantGraph(self):
        signal_name = self.gui.sinusoidal_list_comboBox.currentText()
        if signal_name != "":
            self.gui.sinusoidal_list_comboBox.removeItem(self.gui.sinusoidal_list_comboBox.currentIndex())
            signal = storage.componentSin[signal_name]
            signal.subtract_sig_from_result()
            del storage.componentSin[signal_name]
            self.gui.resultant_signalGraph.clear()
            self.gui.composerGraph.clear()

            if len(storage.componentSin) != 0:
                self.gui.resultant_signalGraph.plot(Sinusoidals.resultant_sig[0],Sinusoidals.resultant_sig[1],pen='r'
                                                    )

    def plot_resultant_sig_on_mainGraph(self):
        self.plotOnMain(Sinusoidals.resultant_sig[0], Sinusoidals.resultant_sig[1],
                        "Resultant Signal from Composer")
        IllustratorApplication.export_resultant_as_csv(IllustratorApplication.exported_signal_index)
        # storage.opened_signal["signal_data"] = Sinusoidals.resultant_sig[1]
        Sinusoidals.resultant_sig = [np.linspace(0, 2, 500, endpoint=False), [0] * 500]
        self.gui.resultant_signalGraph.clear()
        self.gui.sinusoidal_list_comboBox.clear()
        storage.componentSin = {}                              
 
    def Renew_Intr(self, Freq):
        try:
            self.Signal_test.get_Interpolation(Freq)
            self.gui.freq_label.setText(str(Freq))
            self.gui.mainGraph.removeItem(self.Dotted_plot)
            self.Dotted_plot = self.gui.mainGraph.plot(self.Signal_test.Time_Intrv, self.Signal_test.Samples, pen="k",
                                                       symbol='+')
            self.gui.secondaryGraph.clear()
            self.gui.secondaryGraph.plot(self.Signal_test.TimeAxis, IllustratorApplication.interpolate_f, pen="b")
            self.gui.secondryGraph_info.setText("[Sampling frq. :"+str(Freq)+"]")
        except:
            pass

    @classmethod
    def export_resultant_as_csv(cls, file_name="signal_data"):
        df = pd.DataFrame(Sinusoidals.resultant_sig).transpose()
        df.columns = ['Time', 'Amplitude']
        df.to_csv(file_name + '.csv', index=False)


    def plotOnMain(self, Time, Amplitude, Name):
        
        self.Signal_test = Test_Signal(Time, Amplitude)
        self.gui.mainGraph.clear()
        self.gui.secondaryGraph.clear()

        self.gui.samplingFreq_Slider.setMaximum(3 * self.Signal_test.Max_Freq)
        self.gui.mainGraph.plot(Time, Amplitude, pen="r")
        self.gui.mainGraph_info.setText("["+Name+" /Max.frq. : "+str(self.Signal_test.Max_Freq)+"Hz]")
        self.gui.mainGraph.setXRange(0, max(self.Signal_test.TimeAxis), padding=0)

        self.gui.secondaryGraph.setXRange(0, max(self.Signal_test.TimeAxis), padding=0)

    @classmethod
    def return_zero_at_emptyString(cls, string):
        if string == "":
            return "0"
        else:
            return string


class Sinusoidals():
    resultant_sig = [np.linspace(0, 2, 1000, endpoint=False), [0] * 1000]

    def __init__(self, name="", frequency=1, amplitude=1, phase=0):
        self.name = name
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = phase
        self.time = np.linspace(0, 2, 1000, endpoint=False)
        self.y_axis_value = amplitude * np.sin(2 * math.pi * frequency * self.time + phase)

    def add_sig_to_result(self):
        for point in range(1000):
            Sinusoidals.resultant_sig[1][point] += self.y_axis_value[point]

    def subtract_sig_from_result(self):
        for point in range(1000):
            Sinusoidals.resultant_sig[1][point] -= self.y_axis_value[point]


class storage():
    componentSin = {}


class Test_Signal(object):

    def __init__(self, XAxis, YAxis):
        self.Time_Intrv = 0
        self.Samples = []
        self.TimeAxis = XAxis
        self.amplitude = YAxis
        self.sample_rate = int(len(self.TimeAxis) / max(self.TimeAxis))
        self.Power = list(np.abs(fft(self.amplitude)))
        self.FreQList = []
        self.Freq = list(np.abs(fftfreq(len(self.TimeAxis), 1 / self.sample_rate)))
        self.Max_Freq = self.get_maxFreq()
        print(self.Max_Freq)
        self.get_Interpolation(1)

    def get_Interpolation(self, freq):
        Ts = 1 / freq
        Time_Values = []
        self.Samples = []
        Step_in_index = int(np.ceil(len(self.TimeAxis)) / (max(self.TimeAxis) * freq))
        for index in range(0, len(self.TimeAxis), Step_in_index):
            self.Samples.append(self.amplitude[index])
            Time_Values.append(self.TimeAxis[index])
            # I will plot the pints{Time_Values,self.Samples } in the same main graph as a points
        IllustratorApplication.interpolate_f = 0  # class Variable
        num_points = len(Time_Values)  # sample points
        self.Time_Intrv = Time_Values
        for index in range(0, num_points):  # interpolation with sinc function
            IllustratorApplication.interpolate_f += self.Samples[index] * np.sinc(
                (np.array(self.TimeAxis) - Ts * index) / Ts)

    def get_maxFreq(self):
        for index in range(1, len(self.Freq) // 2):
            if (1e-1 < self.Power[index] - self.Power[index - 1]) and (
                    1e-1 < self.Power[index] - self.Power[index + 1]):
                self.FreQList.append(self.Freq[index])
        return int(self.FreQList[-1])


import sys


def window():
    app = QApplication(sys.argv)
    win = IllustratorApplication()

    win.show()
    sys.exit(app.exec_())


# main code
if __name__ == "__main__":
    window()
