#include "SettingsWindow.h"


SettingsWindow::SettingsWindow(QWidget* parent, const QJsonObject current_settings)
    : QDialog(parent), settings(current_settings)
{
    ui.setupUi(this);
    initUI();
    updateLayout();
}

SettingsWindow::~SettingsWindow() {}

void SettingsWindow::initUI()
{
    setWindowTitle("Advanced settings");
    connect(ui.saveButton, &QPushButton::clicked, this, [this]() {this->settings = refreshSettings(); accept(); });
    connect(ui.filterBox, &QCheckBox::clicked, this, [this](bool checked) {ui.filterWindowSpinBox->setEnabled(checked); });
    bool filterOn = this->settings["report"].toObject()["filtering"].toObject()["median_filter"].toBool(false);
    if (filterOn) {
        ui.filterWindowSpinBox->setEnabled(true);
    }
    else {
        ui.filterWindowSpinBox->setEnabled(false);
    }

	QString start_time = this->settings["data"].toObject()["start_time"].toString();
	QString end_time = this->settings["data"].toObject()["end_time"].toString();

	QDateTime startDT = QDateTime::fromString(start_time, "yyyy-MM-dd HH:mm:ss");
	QDateTime endDT = QDateTime::fromString(end_time, "yyyy-MM-dd HH:mm:ss");

    // Compute the difference in hours:
	/*int hoursDiff = startDT.secsTo(endDT) / 3600;
	if (hoursDiff < 24) {
        this->settings["report"].toObject()["layout"].toObject()["auto_page_generation"] = true;
        this->settings["report"].toObject()["layout"].toObject()["multipage"] = false;
		ui.pageGenerationAutomaticButton->setChecked(true);
		ui.pageGenerationManualButton->setChecked(false);
		ui.multipageButton->setChecked(false);
		ui.singlePageButton->setChecked(true);

		ui.multipageButton->setEnabled(false);
		ui.singlePageButton->setEnabled(false);
		ui.pageGenerationAutomaticButton->setEnabled(false);
		ui.pageGenerationManualButton->setEnabled(false);

	}*/
	setFixedSize(size());
	setWindowIcon(QIcon(":/logo/nappa_icon.png"));
}

void SettingsWindow::updateLayout()
{
    const auto reportSettings = this->settings["report"].toObject();

    const auto classifier_input = reportSettings["classifier_input"].toObject();
    const auto filtering = reportSettings["filtering"].toObject();
    const auto layout = reportSettings["layout"].toObject();
    const auto output_formats = reportSettings["output_formats"].toObject();
    const auto quality = reportSettings["quality"].toObject();

    ui.fullFeaturesButton->setChecked(!(classifier_input["accelerometer_only"].toBool(false)));
    ui.accelerometerOnlyButton->setChecked(classifier_input["accelerometer_only"].toBool(false));

    ui.filterNonwearBox->setChecked(filtering["nonwear"].toBool(false));
    ui.filterBox->setChecked(filtering["median_filter"].toBool(false));
    ui.filterWindowSpinBox->setValue(filtering["window_size"].toInt(19));

    ui.pageGenerationAutomaticButton->setChecked(layout["auto_page_generation"].toBool(true));
    ui.pageGenerationManualButton->setChecked(!layout["auto_page_generation"].toBool(true));

    ui.multipageButton->setChecked(layout["multipage"].toBool(false));
    ui.singlePageButton->setChecked(!layout["multipage"].toBool(false));

    ui.csvOutputBox->setChecked(output_formats["csv"].toBool(true));
    ui.pdfOutputBox->setChecked(output_formats["pdf"].toBool(true));
    ui.figuresOutputBox->setChecked(output_formats["figures"].toBool(true));

    ui.reportQualityBox->setValue(quality["dpi"].toInt(100));
    ui.xTicksBox->setValue(quality["x_axis_ticks"].toInt(8));
    ui.logScaleBox->setChecked(quality["log_scale"].toBool(true));
    ui.dateStyleBox->setCurrentIndex(quality["date_format"].toInt(0));
}

QJsonObject SettingsWindow::refreshSettings()
{
    /* Structure of report part in settings:
    "report": {
        "classifier_input": {
            "accelerometer_only": false
        },
        "filtering": {
            "exclude_nonwear": false,
            "filter_window_size": 19,
            "use_median_filter": true
        },
        "layout": {
            "auto_page_generation": true,
            "multipage": false
        },
        "output_formats": {
            "csv": true,
            "figures": true,
            "pdf": true
        },
        "quality": {
            "date_format": 0,
            "dpi": 100,
            "log_scale": true,
            "x_axis_ticks": 8
        }
    }
    */
    // Subfields of the report "advanced" settings.
    QJsonObject quality;
    quality["dpi"] = ui.reportQualityBox->value();
    quality["x_axis_ticks"] = ui.xTicksBox->value();
    quality["date_format"] = ui.dateStyleBox->currentIndex();
    quality["log_scale"] = ui.logScaleBox->isChecked();

    QJsonObject filtering;
    filtering["median_filter"] = ui.filterBox->isChecked();
    filtering["window_size"] = ui.filterWindowSpinBox->value();
    filtering["nonwear"] = ui.filterNonwearBox->isChecked();

    QJsonObject outputFormats;
    outputFormats["pdf"] = ui.pdfOutputBox->isChecked();
    outputFormats["csv"] = ui.csvOutputBox->isChecked();
    outputFormats["figures"] = ui.figuresOutputBox->isChecked();

    QJsonObject layout;
    layout["auto_page_generation"] = ui.pageGenerationAutomaticButton->isChecked();
    layout["multipage"] = ui.multipageButton->isChecked();

    QJsonObject classifierInput;
    classifierInput["accelerometer_only"] = !ui.fullFeaturesButton->isChecked();

    QJsonObject report;
    report["quality"] = quality;
    report["filtering"] = filtering;
    report["output_formats"] = outputFormats;
    report["layout"] = layout;
    report["classifier_input"] = classifierInput;

    this->settings["report"] = report;

    return settings;
}
void SettingsWindow::mergeSettings(const QJsonObject& patch)
{
    for (auto it = patch.begin(); it != patch.end(); ++it)
        settings[it.key()] = it.value();
}