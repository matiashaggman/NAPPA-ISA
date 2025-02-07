# Copyright BABA center 2025

import tempfile
import os
import sys
import json
import zipfile

from shutil import rmtree

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QGridLayout, QDateTimeEdit, QLabel, QDialog, QCheckBox

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime
from PyQt5.QtGui import QIcon

from nappa_gui.main_window_ui import Ui_NappaDialog

from nappa_isa_main import nappa_analysis, load_data, detect_wear, detect_wear_blocks
from nappa.update import check_for_update, do_update

tempfolder = tempfile.gettempdir() + '\\NAPPA-ISA'

CURRENT_VERSION = 1.0

# Separate thread runner for various functions.
# This is used to prevent the main window from freezing when running analysis.
class Worker(QThread):
    status_update = pyqtSignal(str)
    analysis_finished = pyqtSignal(str)
    import_finished = pyqtSignal(object) 

    def __init__(self, recording=None, input_file=None, output_file=None, options=None, call_type=None):
        super().__init__()

        self.status_callback = self.status_update.emit

        # This is prepended before the file path if dropped to the window
        #  (at least in windows machines), needs to be removed manually.
        dragdrop_prefix = 'file:///'

        self.recording = recording
        self.options = options
        self.call_type = call_type

        if input_file is not None:
            if dragdrop_prefix in input_file:
                self.input_file = input_file.split(dragdrop_prefix)[1] # Remove file path prefix
            else:
                self.input_file = input_file

        if output_file is not None:
            if dragdrop_prefix in output_file:
                self.output_file = output_file.split(dragdrop_prefix)[1]
            else:
                self.output_file = output_file

        return

    def run(self):
        if self.call_type == 'analysis':
            nappa_analysis(recording=self.recording, output_file=self.output_file, tempfolder=tempfolder,
                            options=self.options, status_callback=self.status_callback)
            self.analysis_finished.emit(self.output_file)

        elif self.call_type == 'import':
            try:
                if os.path.isdir(tempfolder):
                    rmtree(tempfolder)
            except Exception as e:
                QMessageBox.critical(None, 'Error', str(e))
                return
            try:
                with zipfile.ZipFile(self.input_file, "r") as zip_ref:
                    zip_ref.extractall(tempfolder)
            except Exception as e:
                QMessageBox.critical(None, 'Error', str(e))
                return
            sleepRecording = load_data(tempfolder, time_offset=self.options['time_offset'])
            self.import_finished.emit(sleepRecording)
        return

class TimeDateGridWindow(QDialog):
    def __init__(self, periods):
        super().__init__()
        self.setWindowTitle("Select sleep periods for individual report pages.")

        self.periods = []
        self.checkboxes = []
        self.layout = QGridLayout()

        self.date_time_edits = []
        for i, (start, end) in enumerate(periods):

            date_time_edit_start = QDateTimeEdit()
            date_time_edit_end = QDateTimeEdit()
            checkbox = QCheckBox("Include")
            
            start = QDateTime.fromString(start, "yyyy-MM-dd HH:mm:ss")
            end = QDateTime.fromString(end, "yyyy-MM-dd HH:mm:ss")

            date_time_edit_start.setDateTime(start)
            date_time_edit_end.setDateTime(end)
            checkbox.setChecked(True)

            labelStart = QLabel("Start:")
            labelEnd = QLabel("End:")

            date_time_edit_start.setCalendarPopup(True)
            date_time_edit_end.setCalendarPopup(True)

            row = i

            self.layout.addWidget(labelStart, row, 0)
            self.layout.addWidget(date_time_edit_start, row, 1)
            self.layout.addWidget(labelEnd, row, 2)
            self.layout.addWidget(date_time_edit_end, row, 3)
            self.layout.addWidget(checkbox, row, 4)

            self.date_time_edits.append((date_time_edit_start, date_time_edit_end))
            self.checkboxes.append(checkbox)

        self.setLayout(self.layout)


    def closeEvent(self, event):
        for (start_edit, end_edit), checkbox in zip(self.date_time_edits, self.checkboxes):
            if checkbox.isChecked():
                start = start_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
                end = end_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
                self.periods.append([start, end])

        self.accept()
        return



class NappaMainWindow(QMainWindow, Ui_NappaDialog):
    def __init__(self):
        super().__init__()

        # if check_for_update(CURRENT_VERSION):
        #     reply = QMessageBox.question(None, 'Update found', 'An updated version of the software was found. Do you want to download and install?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        #     if reply == QMessageBox.Yes:
        #         do_update(CURRENT_VERSION)
        #     else:
        #         return
                
        self.sleepRecording = None

        self.setupUi(self)
        self.initUI()
        self.setFixedSize(self.size())
        self.setWindowIcon(QIcon(":/logo/nappa_icon.png"))
        
        # Reference to the secondary window
        self.time_date_grid_window = None

        # Load settings from drive:
        self.options = load_options('options.json')
        self.initOptions()

        self.worker = Worker(call_type='check_for_update')  
        self.worker.start()
        return

    def initUI(self):
        self.setAcceptDrops(True)
        self.browseInput.clicked.connect(self.selectInputFile)
        self.browseOutput.clicked.connect(self.selectOutputFile)
        self.analyzeButton.clicked.connect(self.analyzeRecording)
        self.selectPeriodsButton.clicked.connect(self.selectPeriods)
        self.pageGenerationAutomaticButton.toggled.connect(self.pageGenerationManualButtonToggled)
        self.pageGenerationManualButton.toggled.connect(self.pageGenerationAutomaticButtonToggled)
        self.timeOffsetSpinBox.valueChanged.connect(self.timeOffsetSpinBoxValueChanged)

        self.durationLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.sleepPeriodsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.startTimeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.endTimeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)

        self.versionLabel.setText(f'version: {CURRENT_VERSION}')
        return

    def pageGenerationManualButtonToggled(self):
        if self.pageGenerationManualButton.isChecked():
            self.selectPeriodsButton.setEnabled(True)
        return
    
    def pageGenerationAutomaticButtonToggled(self):
        if self.pageGenerationAutomaticButton.isChecked():
            self.selectPeriodsButton.setEnabled(False)
            if self.sleepRecording is not None:
                wear_idx = detect_wear(self.sleepRecording.features.loc[:, 'activity'])
                self.options['sleep_periods'] = detect_wear_blocks(wear_idx)
        return
    
    def timeOffsetSpinBoxValueChanged(self):
        offset = int(self.timeOffsetSpinBox.value())
        if offset >= 0:
            self.startTimeLabel.setText(f'Start time (UTC+{offset})')
            self.endTimeLabel.setText(f'End time (UTC+{offset})')
        else:
            self.startTimeLabel.setText(f'Start time (UTC{offset})')
            self.endTimeLabel.setText(f'End time (UTC{offset})')

        current_offset = self.options.get('time_offset', 0)
        start_time = self.startTime.dateTime().addSecs((offset - current_offset) * 3600)
        end_time = self.endTime.dateTime().addSecs((offset - current_offset) * 3600)
        self.startTime.setDateTime(start_time)
        self.endTime.setDateTime(end_time)

        adjusted_periods = []
        for (period_start, period_end) in self.options['sleep_periods']:
            period_start = QDateTime.fromString(period_start, "yyyy-MM-dd HH:mm:ss")
            period_end = QDateTime.fromString(period_end, "yyyy-MM-dd HH:mm:ss")

            period_start = period_start.addSecs((offset - current_offset) * 3600)
            period_end = period_end.addSecs((offset - current_offset) * 3600)
            
            period_start = period_start.toString("yyyy-MM-dd HH:mm:ss")
            period_end = period_end.toString("yyyy-MM-dd HH:mm:ss")
            adjusted_periods.append((period_start, period_end))

        self.options['time_offset'] = offset
        self.options['sleep_periods'] = adjusted_periods
        return
       
    def selectInputFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", "Zip Files (*.zip)", options=options)
        if file:
            self.inputFile.setText(file)
            self.importRecording()
        return

    def selectOutputFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file, _ = QFileDialog.getSaveFileName(self, "Select Output File", "", "Zip Files (*.zip)", options=options)
        if file:
            self.outputFile.setText(file)
        return

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
        return

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.inputFile.setText(file_path)
            self.outputFile.setText(file_path[:-4] + '_analyzed.zip')
            self.importRecording()
        else:
            event.ignore()
        return
      
    def initOptions(self):
        
        self.timeOffsetSpinBox.setValue(self.options['time_offset'])
        
        self.filterBox.setChecked(self.options['median_filter'])
        self.logScaleBox.setChecked(self.options['log_scale'])
        self.filterWindowSpinBox.setValue(self.options['filter_window'])
        self.reportQualityBox.setValue(self.options['report_dpi'])
        self.xTicksBox.setValue(self.options['x_ticks'])
        self.filterNonwearBox.setChecked(self.options['filter_nonwear'])

        self.fullFeaturesButton.setChecked(self.options['full_features'])
        self.accelerometerOnlyButton.setChecked(self.options['full_features'] == False)

        self.csvOutputBox.setChecked(self.options['csv_output'])
        self.pdfOutputBox.setChecked(self.options['pdf_output'])

        self.multipageButton.setChecked(self.options['multipage'])
        self.singlePageButton.setChecked(self.options['multipage'] == False)
        
        self.pageGenerationAutomaticButton.setChecked(self.options['page_generation_automatic'])
        self.pageGenerationManualButton.setChecked(self.options['page_generation_automatic'] == False)
        self.selectPeriodsButton.setEnabled(self.pageGenerationManualButton.isChecked())

        self.sdtConfidenceSummaryBox.setChecked(self.options['plots']['sdt_ci'])
        self.sdtSummaryBox.setChecked(self.options['plots']['sdt'])
        self.sdtSubsqBox.setChecked(self.options['plots']['subsequent_sdt'])

        self.discreteHypnogramSummaryBox.setChecked(self.options['plots']['sdt'] == False)
        self.discreteHypnogramSubsqBox.setChecked(self.options['plots']['subsequent_sdt'] == False)

        self.activitySummaryBox.setChecked(self.options['plots']['activity'])
        self.respirationSummaryBox.setChecked(self.options['plots']['respiration_rate'])
        self.positionSummaryBox.setChecked(self.options['plots']['position'])

        self.positionSubsqBox.setChecked(self.options['plots']['subsequent_position'])
        self.respirationSubsqBox.setChecked(self.options['plots']['subsequent_respiration_rate'])
        self.activitySubsqBox.setChecked(self.options['plots']['subsequent_activity'])
        self.donutSubsqBox.setChecked(self.options['plots']['donut'])

        self.violinRadioButton.setChecked(self.options['plots']['summary_fig'] == 'violin')
        self.barRadioButton.setChecked(self.options['plots']['summary_fig'] == 'bar')

        return self
    
    def refreshOptions(self):

        self.options['start_time']      = self.startTime.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.options['end_time']        = self.endTime.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.options['time_offset']     = int(self.timeOffsetSpinBox.value())

        self.options['report_dpi']      = int(self.reportQualityBox.value())
        self.options['x_ticks']         = int(self.xTicksBox.value())
        self.options['date_style']      = self.dateStyleBox.currentIndex()
        
        self.options['filter_nonwear']  = self.filterNonwearBox.isChecked()
        self.options['log_scale']       = self.logScaleBox.isChecked()
        self.options['median_filter']   = self.filterBox.isChecked()
        self.options['filter_window']   = int(self.filterWindowSpinBox.value())

        self.options['csv_output']      = self.csvOutputBox.isChecked()
        self.options['pdf_output']      = self.pdfOutputBox.isChecked()
        
        self.options['full_features']   = self.fullFeaturesButton.isChecked()
        self.options['multipage']       = self.multipageButton.isChecked()
        self.options['page_generation_automatic'] = self.pageGenerationAutomaticButton.isChecked()

        self.options['plots']['summary_fig'] = 'bar' if self.barRadioButton.isChecked() else 'violin'
        self.options['plots']['sdt_ci']      = self.sdtConfidenceSummaryBox.isChecked()
        self.options['plots']['sdt']         = self.sdtSummaryBox.isChecked()
        self.options['plots']['activity']    = self.activitySummaryBox.isChecked()
        self.options['plots']['respiration_rate'] = self.respirationSummaryBox.isChecked()
        self.options['plots']['position']    = self.positionSummaryBox.isChecked()
        self.options['plots']['donut']       = self.donutSubsqBox.isChecked()

        self.options['plots']['subsequent_sdt']         = self.sdtSubsqBox.isChecked()
        self.options['plots']['subsequent_activity']    = self.activitySubsqBox.isChecked()
        self.options['plots']['subsequent_respiration_rate'] = self.respirationSubsqBox.isChecked()
        self.options['plots']['subsequent_position']    = self.positionSubsqBox.isChecked()

        return self
    
    def selectPeriods(self):
        time_date_grid_window = TimeDateGridWindow(self.options['sleep_periods'])
        if time_date_grid_window.exec_() == QDialog.Accepted:
            self.options['sleep_periods'] = time_date_grid_window.periods
            self.sleepPeriodsLabel.setText(f'{len(time_date_grid_window.periods)}')
        return

    def updateStatus(self, status):
        self.statusLabel.setText(status)
        return

    def importRecording(self):
        self.refreshOptions()
        self.statusLabel.setText('Importing sleep recording...')
        input_file = self.inputFile.text()
        # Start the worker thread. Use a separate thread to prevent th main window from freezing.
        self.worker = Worker(input_file=input_file, output_file=None, options=self.options, call_type='import')  
        self.worker.import_finished.connect(self.onImportComplete)
        self.worker.start()
        return
    
    def onImportComplete(self, sleepRecording):
        if sleepRecording is not None:
            self.sleepRecording = sleepRecording
            wear_idx = detect_wear(self.sleepRecording.features.loc[:, 'activity'])
            self.options['sleep_periods']= detect_wear_blocks(wear_idx)
            
            self.startTime.setDateTime(QDateTime(sleepRecording.start))
            self.endTime.setDateTime(QDateTime(sleepRecording.end))
            self.startTime.setEnabled(True)
            self.endTime.setEnabled(True)
            self.analyzeButton.setEnabled(True)    

            self.durationLabel.setText(f'{str(self.sleepRecording.duration)[:-6]} hours')
            self.statusLabel.setText('Status: sleep recording imported.')
            self.sleepPeriodsLabel.setText(f'{len(self.options['sleep_periods'])}')
            
        else:
            self.inputFile.setText('')
            self.outputFile.setText('')
            QMessageBox.critical(self, 'Invalid Input', 'Input zip file must only contain accelerometer and gyroscope feature files in a .csv format.')
        
        return

    def analyzeRecording(self):

        self.refreshOptions()
        input_file = self.inputFile.text()
        output_file = self.outputFile.text()
        if not input_file or not output_file:
            QMessageBox.warning(self, "Error", "Please specify both input and output files.")
            return
        else: 
            self.setDisabled(True)
            self.setWindowTitle("Analyzing, please wait...")
            
            # Start the worker thread. Use a separate thread to prevent th main window from freezing.
            self.worker = Worker(recording=self.sleepRecording, output_file=output_file,
                                options=self.options, call_type='analysis')
            
            self.worker.status_update.connect(self.updateStatus)
            self.worker.analysis_finished.connect(self.onAnalysisComplete)
            self.worker.start()
        return 

    def onAnalysisComplete(self, output_file):
    
        self.setWindowTitle("NAPPA Infant Sleep Analyzer")
        QMessageBox.information(self, "Analysis Complete", f"Output saved to {output_file}.")
        self.statusLabel.setText('Status: awaiting user input.')
        self.setDisabled(False)
        return

    def closeEvent(self, event):
        self.refreshOptions()
        try:
            with open('options.json', 'w') as json_file:
                json.dump(self.options, json_file, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save options: {str(e)}")

        # Clean up tmp dir:
        if os.path.isdir(tempfolder):
            rmtree(tempfolder)

        event.accept()
        return
    

def load_options(options_path):
    with open(options_path, 'r') as file:
        settings = json.load(file)
    return settings

# Entry point
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = NappaMainWindow()
    mainWin.show()
    sys.exit(app.exec_())