#include "NappaMainWindow.h"

#include <QFileDialog>
#include <QMimeData>
#include <QFile>
#include <QJsonDocument>
#include <QJsonParseError>
#include <QJsonArray>
#include <QJsonObject>
#include <QJsonValue>
#include <QMessageBox>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QDragEnterEvent>  
#include <QDropEvent>
#include <QVBoxLayout>


NappaMainWindow::NappaMainWindow(QWidget* parent)
    : QDialog(parent), timeGridWindow(nullptr)
{
    ui.setupUi(this);
    setWindowTitle("NAPPA Infant Sleep Analyzer Client");
    setWindowIcon(QIcon(":/logo/nappa_icon.png"));
    setFixedSize(size());

    loadSettings(this->settingsPath);
    initUI();

    connect(this, &NappaMainWindow::connectToServerAndFetchUpdate, this, &NappaMainWindow::connectToServerAndFetchUpdate);
    NappaMainWindow::fetchPublicIP();
}

NappaMainWindow::~NappaMainWindow()
{
    this->refreshSettings();

	// Reset recording specific settings to null values at the start of the application:
    QJsonObject data;
    data["sleep_periods"] = QJsonArray();
    this->settings["data"] = data;
    this->saveSettings(this->settingsPath);
}

void NappaMainWindow::initUI()
{
    connect(ui.browseInputButton, &QPushButton::clicked, this, &NappaMainWindow::onBrowseInputButtonClicked);
    connect(ui.browseOutputButton, &QPushButton::clicked, this, &NappaMainWindow::onBrowseOutputButtonClicked);
    connect(ui.selectPeriodsButton, &QPushButton::clicked, this, &NappaMainWindow::onSelectPeriodsButtonClicked);
	connect(ui.advancedSettingsButton, &QPushButton::clicked, this, &NappaMainWindow::onAdvancedSettingsButtonClicked);
	connect(ui.UtcOffsetApplyButton, &QPushButton::clicked, this, &NappaMainWindow::onUtcOffsetApplyButtonClicked);
	connect(ui.analyzeButton, &QPushButton::clicked, this, &NappaMainWindow::onAnalyzeButtonClicked);

    this->setAcceptDrops(false);
	ui.browseInputButton->setEnabled(false);
	ui.browseOutputButton->setEnabled(false);
	ui.analyzeButton->setEnabled(false);
	ui.UtcOffsetApplyButton->setEnabled(false);
	ui.appVersionLabel->setText("App version: " + this->version);
	
}

void NappaMainWindow::dragEnterEvent(QDragEnterEvent* event) {
    if (event->mimeData()->hasUrls()) {
        event->acceptProposedAction(); // Accept drag if it's a file
    }
}

void NappaMainWindow::dropEvent(QDropEvent* event) {
    const QList<QUrl> urls = event->mimeData()->urls();
    if (urls.isEmpty())
        return;

    QString inputFile = urls.first().toLocalFile();
    if (!inputFile.isEmpty()) {
        ui.inputFile->setText(inputFile);
        // Use QFileInfo::completeBaseName() to handle filenames with dots and spaces correctly
        QString file = QFileInfo(inputFile).completeBaseName();
        QString dir = QFileInfo(inputFile).absolutePath();
        QString outputFile = dir + "/" + file + "_analyzed.zip";
        ui.outputFile->setText(outputFile);
		this->importRecording();
    }
}

void NappaMainWindow::onAdvancedSettingsButtonClicked() {

    SettingsWindow settingsWindow(this, this->settings);

    if (settingsWindow.exec() == QDialog::Accepted) {

        this->settings["report"] = settingsWindow.refreshSettings()["report"];
		
        this->refreshSettings();
        this->saveSettings(this->settingsPath);
    }
}

void NappaMainWindow::onBrowseInputButtonClicked()
{
    QString inputFile = QFileDialog::getOpenFileName(this, "Select Input File", "", "Zip Files (*.zip)");
    if (!inputFile.isEmpty()) {
        ui.inputFile->setText(inputFile);

        // Remove .zip from input file and append _analyzed.zip instead:
		QString file = QFileInfo(inputFile).baseName();
		QString dir = QFileInfo(inputFile).absolutePath();
		QString outputFile = dir + "/" + file + "_analyzed.zip";
		ui.outputFile->setText(outputFile);
        this->importRecording();
    }
}

void NappaMainWindow::onBrowseOutputButtonClicked()
{
    QString file = QFileDialog::getSaveFileName(this, "Select Output File", "", "Zip Files (*.zip)");
    if (!file.isEmpty()) {
        ui.outputFile->setText(file);
    }
}

void NappaMainWindow::onSelectPeriodsButtonClicked() {
    QList<QPair<QString, QString>> currentPeriods;

    if (settings.contains("data") && settings["data"].isObject()) {
        QJsonObject dataObject = settings["data"].toObject();
        if (dataObject.contains("sleep_periods") && dataObject["sleep_periods"].isArray()) {
            QJsonArray periodsArray = dataObject["sleep_periods"].toArray();

            for (const QJsonValue& val : periodsArray) {
                if (val.isArray()) {
                    QJsonArray pair = val.toArray();
                    if (pair.size() == 2) {
                        QString start = pair[0].toString();
                        QString end = pair[1].toString();
                        currentPeriods.append(qMakePair(start, end));
                    }
                }
            }
        }
    }

    TimeDateGridWindow dialog(this);
    dialog.loadPeriods(currentPeriods);

    if (dialog.exec() == QDialog::Accepted) {
        QList<QPair<QString, QString>> selectedPeriods = dialog.periods;

        if (selectedPeriods.isEmpty())
            return;

        QJsonArray newPeriodsArray;
        for (const auto& pair : selectedPeriods) {
            QJsonArray onePeriod;
            onePeriod.append(pair.first);
            onePeriod.append(pair.second);
            newPeriodsArray.append(onePeriod);
        }

        // Update settings with new periods  
        if (settings.contains("data") && settings["data"].isObject()) {
            QJsonObject dataObject = settings["data"].toObject();
            dataObject["sleep_periods"] = newPeriodsArray;
			this->settings["data"] = dataObject;
			this->refreshSettings();
			this->saveSettings(this->settingsPath);
		}

        if (settings["report"].toObject()["layout"].toObject()["auto_page_generation"].toBool()) {
			QMessageBox::warning(this, "Page generation",
                "Warning: Automatic page generation is currently enabled.\n\n"
                "To prevent your manually defined sleep periods from being overwritten, "
                "please go to Advanced Settings and switch the page generation mode from Automatic to Manual.");
        }
        ui.sleepPeriodsLabel->setText(QString::number(selectedPeriods.size()));
        QDateTime startDT = QDateTime::fromString(selectedPeriods[0].first, "yyyy-MM-dd HH:mm:ss");
        QDateTime endDT = QDateTime::fromString(selectedPeriods[selectedPeriods.size() - 1].second, "yyyy-MM-dd HH:mm:ss");
        
		ui.startTime->setDateTime(startDT);
		ui.endTime->setDateTime(endDT);
        this->saveSettings(this->settingsPath);
    }
}

void NappaMainWindow::onUtcOffsetApplyButtonClicked()
{
    this->importRecording();
}

void NappaMainWindow::onAnalyzeButtonClicked()
{
    ui.analysisStatusLabel->setText("Status: Analyzing sleep recording...");
    this->refreshSettings();
    this->saveSettings(this->settingsPath);
	ui.analyzeButton->setEnabled(false);
    ThreadWorker* worker = new ThreadWorker(
        this,
        this->ui.inputFile->text(),
        this->ui.outputFile->text(),
        this->settingsPath,
        this->userData,
        ThreadWorker::Analysis
    );
    connect(worker, &ThreadWorker::finished, worker, &QObject::deleteLater);
    connect(worker, &ThreadWorker::onUpdateStatus, this, &NappaMainWindow::onUpdateStatus);
    worker->start();
}

void NappaMainWindow::onUpdateStatus(const float statusCode, const QString& msg)
{

	if (statusCode == STATUS_USER_CONNECTED) {
		ui.appStatusLabel->setText("App status: Connected to server.");
		this->setAcceptDrops(true);
		ui.browseInputButton->setEnabled(true);
		ui.browseOutputButton->setEnabled(true);
	}
    else if (statusCode == STATUS_USER_CONNECT_ERROR) {
        ui.appStatusLabel->setText("App status: Connection error.");
		QMessageBox::critical(nullptr, "Error", "Failed to connect to server: " + msg);
        this->setAcceptDrops(false);
        ui.browseInputButton->setEnabled(false);
        ui.browseOutputButton->setEnabled(false);
        ui.analyzeButton->setEnabled(false);
    }
	else if (statusCode == STATUS_IMPORT_SUCCESS) {
		ui.analysisStatusLabel->setText("Status: Recording imported successfully.");
        this->setEnabled(true);
		this->ui.analyzeButton->setEnabled(true);
	}
	else if (statusCode == STATUS_IMPORT_ERROR) {
		ui.analysisStatusLabel->setText("Status: Import error. ");
		QMessageBox::critical(nullptr, "Error", "Failed to import recording:\n" + msg);
        this->setEnabled(true);
		this->ui.analyzeButton->setEnabled(false);
		this->ui.startTime->setEnabled(false);
		this->ui.endTime->setEnabled(false);
		this->ui.inputFile->setText("");
		this->ui.outputFile->setText("");
	}
	else if (statusCode == STATUS_ANALYZE_ERROR) {
		ui.analysisStatusLabel->setText("Status: Analysis error.");
		QMessageBox::critical(nullptr, "Error", "Failed to analyze recording: " + msg);
		ui.analyzeButton->setEnabled(true);
	}
	else if (statusCode == STATUS_ANALYZE_SUCCESS) {
		ui.analysisStatusLabel->setText("Status: Analysis finished successfully.");
		QMessageBox::information(nullptr, "Success", "Analysis finished successfully. Output saved to:\n\n"
			+ this->ui.outputFile->text());
		ui.analyzeButton->setEnabled(true);
	}
}

void NappaMainWindow::onImportFinished(const QJsonObject& response)
{
    if (response.contains("sleep_periods")) {
        QJsonArray sleepPeriods = response["sleep_periods"].toArray();
        QList<QPair<QString, QString>> periods;
        for (const QJsonValue& val : sleepPeriods) {
            if (val.isArray()) {
                QJsonArray pair = val.toArray();
                if (pair.size() == 2) {
                    QString start = pair[0].toString();
                    QString end = pair[1].toString();
                    periods.append(qMakePair(start, end));
                }
            }
        }
        if (sleepPeriods.isEmpty()) {
            if (response.contains("start") && response.contains("end")) {
				// If no sleep periods are found, but start and end times are provided, use them to populate the periods
                QString start = response["start"].toString();
                QString end = response["end"].toString();
                periods.append(qMakePair(start, end));
                QJsonArray periodsArray;
                for (const auto& [pStart, pEnd] : periods) {
                    periodsArray.append(QJsonArray{pStart, pEnd});
                }
                sleepPeriods = periodsArray;
            }
            QMessageBox::warning(this, "No sleep periods", "No sleep periods found in the recording. Please check the input, the sleep recording may be corrupted.\n\n" 
                "You can still run the analysis by manually entering each sleep period.");
        }
        // Update settings with new periods
        if (this->settings.contains("data") && this->settings["data"].isObject()) {
            QJsonObject dataObject = this->settings.value("data").toObject();
            dataObject["sleep_periods"] = sleepPeriods;
            this->settings["data"] = dataObject;
        }
        if (response.contains("duration")) {
            QString duration = response["duration"].toString();
            ui.durationLabel->setText(duration.left(duration.length() - 3));
            // get the days count:
            QStringList parts = duration.split(" ");
            QString days = parts[0];
            if (days.toInt() < 1) {
                ui.selectPeriodsButton->setEnabled(false);
            }
            else {
                ui.selectPeriodsButton->setEnabled(true);
            }
        }
        ui.sleepPeriodsLabel->setText(QString::number(periods.size()));
        QDateTime startDT = QDateTime::fromString(periods[0].first, "yyyy-MM-dd HH:mm:ss");
        QDateTime endDT = QDateTime::fromString(periods[periods.size() - 1].second, "yyyy-MM-dd HH:mm:ss");

        ui.startTime->setDateTime(startDT);
        ui.endTime->setDateTime(endDT);
        ui.startTimeLabel->setText("Start time\n(automatically inferred)");
        ui.endTimeLabel->setText("End time\n(automatically inferred)");
		// center align the labels
		ui.startTimeLabel->setAlignment(Qt::AlignCenter);
		ui.endTimeLabel->setAlignment(Qt::AlignCenter);

		ui.startTime->setEnabled(true);
		ui.endTime->setEnabled(true);
        ui.analyzeButton->setEnabled(true);
		ui.UtcOffsetApplyButton->setEnabled(true);

		this->refreshSettings();
		this->saveSettings(this->settingsPath);
	}
}

void NappaMainWindow::importRecording()
{
    ui.analysisStatusLabel->setText("Status: Importing sleep recording...");
    this->setEnabled(false);
    this->refreshSettings();
    this->saveSettings(this->settingsPath);
    ThreadWorker* worker = new ThreadWorker(
        this,
        this->ui.inputFile->text(),
        this->ui.outputFile->text(),
        this->settingsPath,
        this->userData,
        ThreadWorker::Import
    );
    connect(worker, &ThreadWorker::finished, worker, &QObject::deleteLater);
    connect(worker, &ThreadWorker::onUpdateStatus, this, &NappaMainWindow::onUpdateStatus);
    connect(worker, &ThreadWorker::onImportFinished, this, &NappaMainWindow::onImportFinished);
    worker->start();
}

void NappaMainWindow::refreshSettings() {
    // data part structure in settings:
    /*"data": {
        "end_time": "",
        "sleep_periods": [],
        "start_time": "",
        time_offset: 2
    */

    // Visualization part:
    /*    "visualization": {
        "main_page": {
            "activity": true,
            "position": true,
            "respiration_rate": true,
            "sdt": true,
            "sdt_ci": false,
            "sleep_statistics": false,
            "summaryfig": "violin"
        },
        "subsequent_pages": {
            "activity": true,
            "donut": true,
            "position": true,
            "respiration_rate": true,
            "sdt": true,
            "sdt_ci": false,
            "sleep_statistics": true
        }
    }*/
    QJsonObject data;
    data["sleep_periods"] = this->settings["data"].toObject()["sleep_periods"];

	// Transform time format to yyyy-MM-dd HH:mm:ss
    QDateTime startDT = QDateTime(ui.startTime->date(), ui.startTime->time());
    QDateTime endDT = QDateTime(ui.endTime->date(), ui.endTime->time());
	data["start_time"] = startDT.toString("yyyy-MM-dd HH:mm:ss");;
	data["end_time"] = endDT.toString("yyyy-MM-dd HH:mm:ss");;
    data["time_offset"] = ui.timeOffsetSpinBox->value();

    QJsonObject visualization;
    QJsonObject mainPage;
    mainPage["activity"] = ui.activityMainBox->isChecked();
    mainPage["position"] = ui.positionMainBox->isChecked();
    mainPage["respiration_rate"] = ui.respirationMainBox->isChecked();
    mainPage["sdt"] = ui.sdtMainBox->isChecked();
    mainPage["sdt_ci"] = ui.sdtConfidenceMainBox->isChecked();
    mainPage["sleep_statistics"] = ui.sleepStatisticsMainBox->isChecked();
    mainPage["summaryfig"] = ui.violinRadioButton->isChecked() ? "violin" : "bar";

    QJsonObject subsequentPages;
    subsequentPages["activity"] = ui.activitySubsqBox->isChecked();
    subsequentPages["donut"] = ui.donutSubsqBox->isChecked();
    subsequentPages["position"] = ui.positionSubsqBox->isChecked();
    subsequentPages["respiration_rate"] = ui.respirationSubsqBox->isChecked();
    subsequentPages["sdt"] = ui.sdtSubsqBox->isChecked();
    subsequentPages["sdt_ci"] = ui.sdtConfidenceSubsqBox->isChecked();
    subsequentPages["sleep_statistics"] = ui.sleepStatisticsSubsqBox->isChecked();

    visualization["main_page"] = mainPage;
    visualization["subsequent_pages"] = subsequentPages;

    settings["data"] = data;
    settings["visualization"] = visualization;
}

void NappaMainWindow::loadSettings(const QString& path)
{
    // Settings for main page UI

    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) return;

    QByteArray data = file.readAll();
    QJsonParseError err;
    QJsonDocument doc = QJsonDocument::fromJson(data, &err);
    if (err.error != QJsonParseError::NoError) return;

    this->settings = doc.object();

	// Structure of data settings:
    /*
        "data": {
        "end_time": "",
        "sleep_periods": [
        ],
        "start_time": "",
        "time_offset": 3
    }
    */
	if (settings.contains("data") && settings["data"].isObject()) {
		QJsonObject data_settings = settings["data"].toObject();

		auto utc_offset = data_settings["utc_offset"].toInt(2);
		auto start_time = data_settings["start_time"].toString();
		auto end_time = data_settings["end_time"].toString();

        ui.timeOffsetSpinBox->setValue(utc_offset);
        QDateTime startDT = QDateTime::fromString(start_time, "yyyy-MM-dd HH:mm:ss");
        QDateTime endDT = QDateTime::fromString(end_time, "yyyy-MM-dd HH:mm:ss");

		ui.startTime->setDate(startDT.date());
		ui.endTime->setDate(endDT.date());
        ui.startTime->setTime(startDT.time());
        ui.endTime->setTime(endDT.time());

	}
    // Structure of visualization settings:
    /*
        "visualization": {
            "main_page": {
                "activity": true,
                "position": true,
                "respiration_rate": true,
                "sdt": true,
                "sdt_ci": false,
                "sleep_statistics": false,
                "summaryfig": "violin"
            },
            "subsequent_pages": {
                "activity": false,
                "donut": false,
                "position": false,
                "respiration_rate": false,
                "sdt": true,
                "sdt_ci": false,
                "sleep_statistics": false
            }
        }
     */
	if (settings.contains("visualization") && settings["visualization"].isObject()) {

		if (settings["visualization"].toObject().contains("main_page")) {
			QJsonObject mainPage = settings["visualization"].toObject()["main_page"].toObject();

			ui.activityMainBox->setChecked(mainPage["activity"].toBool(true));
			ui.positionMainBox->setChecked(mainPage["position"].toBool(true));
			ui.respirationMainBox->setChecked(mainPage["respiration_rate"].toBool(true));
			ui.sdtMainBox->setChecked(mainPage["sdt"].toBool(true));
			ui.discreteHypnogramMainBox->setChecked(!mainPage["sdt"].toBool(true));
			ui.sdtConfidenceMainBox->setChecked(mainPage["sdt_ci"].toBool(false));
			ui.sleepStatisticsMainBox->setChecked(mainPage["sleep_statistics"].toBool(true));

            if (mainPage["summaryfig"].toString("bar") == "bar") {
                ui.barRadioButton->setChecked(true);
                ui.violinRadioButton->setChecked(false);
            }
            else {
                ui.violinRadioButton->setChecked(true);
                ui.barRadioButton->setChecked(false);
            }
		}
        if (settings["visualization"].toObject().contains("subsequent_pages")) {
            QJsonObject subsequentPages = settings["visualization"].toObject()["subsequent_pages"].toObject();
            ui.activitySubsqBox->setChecked(subsequentPages["activity"].toBool(true));
            ui.donutSubsqBox->setChecked(subsequentPages["donut"].toBool(true));
            ui.positionSubsqBox->setChecked(subsequentPages["position"].toBool(true));
            ui.respirationSubsqBox->setChecked(subsequentPages["respiration_rate"].toBool(true));
            ui.sdtSubsqBox->setChecked(subsequentPages["sdt"].toBool(true));
            ui.discreteHypnogramSubsqBox->setChecked(!subsequentPages["sdt"].toBool(true));
            ui.sdtConfidenceSubsqBox->setChecked(subsequentPages["sdt_ci"].toBool(false));
            ui.sleepStatisticsSubsqBox->setChecked(subsequentPages["sleep_statistics"].toBool(true));
        }
	}
}

void NappaMainWindow::saveSettings(const QString& path)
{
    this->refreshSettings();
    QFile file(path);
    if (!file.open(QIODevice::WriteOnly)) return;

    QJsonDocument doc(settings);
    file.write(doc.toJson(QJsonDocument::Indented));
}


void NappaMainWindow::fetchPublicIP() {
    QNetworkAccessManager* manager = new QNetworkAccessManager(this);
    QNetworkRequest request(QUrl("https://api.ipify.org?format=text"));

    connect(manager, &QNetworkAccessManager::finished, this, [this](QNetworkReply* reply) {
        if (reply->error() == QNetworkReply::NoError) {
            QString fetchedIP = QString(reply->readAll()).trimmed();
            emit connectToServerAndFetchUpdate(fetchedIP);
        }
        else {
            emit connectToServerAndFetchUpdate("No-ip");
        }
        reply->deleteLater();
        });

    manager->get(request);
	return;
}

void NappaMainWindow::onUpdateRequestFinished(const QJsonObject& response) {
    if (response.contains("version")) {
		auto latest_version = response["version"].toDouble();
        if (latest_version > this->version.toDouble()) {
            QMessageBox::information(this, "Update available", "A new version of ISA is available: " + QString::number(latest_version, 'f', 1) 
                + ". Please visit the github repository to obtain the latest version.");

            ui.appStatusLabel->setText("App status: Update available. Download here:");
            ui.appVersionLabel->setText("App version: " + QString::number(this->version.toDouble(), 'f', 2) + " (outdated)");
        }
        else {
            ui.appVersionLabel->setText("App version: " + QString::number(this->version.toDouble(), 'f', 2) + " (latest)");
		}
    }
}

void NappaMainWindow::connectToServerAndFetchUpdate(const QString& ownIp) {

    this->publicIP = ownIp;
    this->userData["os_version"]    = QSysInfo::prettyProductName();
    this->userData["app_version"]   = this->version;
    this->userData["ip"]            = this->publicIP;

    ThreadWorker* worker = new ThreadWorker(this, "", "", this->settingsPath,
        this->userData, ThreadWorker::Start);
    connect(worker, &ThreadWorker::finished, worker, &QObject::deleteLater);
    connect(worker, &ThreadWorker::onUpdateStatus, this, &NappaMainWindow::onUpdateStatus);
	connect(worker, &ThreadWorker::onUpdateRequestFinished, this, &NappaMainWindow::onUpdateRequestFinished);
    worker->start();

	ui.appStatusLabel->setText("App status: Connecting to server...");
}