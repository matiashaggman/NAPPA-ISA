/********************************************************************************
** Form generated from reading UI file 'main_windowJQkiyT.ui'
**
** Created by: Qt User Interface Compiler version 6.7.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef MAIN_WINDOWJQKIYT_H
#define MAIN_WINDOWJQKIYT_H

#include <QtCore/QVariant>
#include <QtGui/QIcon>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QCheckBox>
#include <QtWidgets/QDateTimeEdit>
#include <QtWidgets/QDialog>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QRadioButton>
#include <QtWidgets/QSpinBox>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_NappaDialog
{
public:
    QGridLayout* gridLayout_5;
    QGroupBox* informationGroupBox;
    QGridLayout* gridLayout_4;
    QLabel* label_4;
    QLabel* appVersionLabel;
    QLabel* githubLabel;
    QLabel* pluginVersionLabel;
    QGroupBox* dataVisualizationGroupBox;
    QGridLayout* gridLayout;
    QTabWidget* tabWidget;
    QWidget* tab;
    QGridLayout* gridLayout_9;
    QGroupBox* sleepMainGroupBox;
    QGridLayout* gridLayout_7;
    QRadioButton* discreteHypnogramMainBox;
    QRadioButton* violinRadioButton;
    QRadioButton* sdtMainBox;
    QRadioButton* barRadioButton;
    QCheckBox* sdtConfidenceMainBox;
    QCheckBox* sleepStatisticsMainBox;
    QGroupBox* sensorDataMainGroupBox;
    QGridLayout* gridLayout_11;
    QCheckBox* activityMainBox;
    QCheckBox* respirationMainBox;
    QCheckBox* positionMainBox;
    QWidget* tab_2;
    QGridLayout* gridLayout_10;
    QGroupBox* sleepSubsqGroupBox;
    QGridLayout* gridLayout_3;
    QRadioButton* discreteHypnogramSubsqBox;
    QCheckBox* donutSubsqBox;
    QRadioButton* sdtSubsqBox;
    QCheckBox* sleepStatisticsSubsqBox;
    QCheckBox* sdtConfidenceSubsqBox;
    QGroupBox* sensorDataSubsqGroupBox;
    QGridLayout* gridLayout_12;
    QCheckBox* activitySubsqBox;
    QCheckBox* respirationSubsqBox;
    QCheckBox* positionSubsqBox;
    QGroupBox* settingsGroupBox;
    QGridLayout* gridLayout_8;
    QLabel* startTimeLabel;
    QLabel* durationLabel;
    QSpinBox* timeOffsetSpinBox;
    QPushButton* selectPeriodsButton;
    QLabel* durationTitleLabel;
    QLabel* utcOffsetLabel;
    QLabel* endTimeLabel;
    QPushButton* advancedSettingsButton;
    QDateTimeEdit* endTime;
    QDateTimeEdit* startTime;
    QLabel* sleepPeriodsTitleLabel;
    QLabel* sleepPeriodsLabel;
    QGroupBox* analysisGroupBox;
    QHBoxLayout* horizontalLayout;
    QLabel* statusLabel;
    QPushButton* analyzeButton;
    QGroupBox* dataGroupBox;
    QGridLayout* gridLayout_2;
    QLineEdit* inputFile;
    QLabel* outputFileLabel;
    QLabel* inputFileLabel;
    QLineEdit* outputFile;
    QPushButton* browseInputButton;
    QPushButton* browseOutputButton;
    QButtonGroup* buttonGroup_2;
    QButtonGroup* buttonGroup;

    void setupUi(QDialog* NappaDialog)
    {
        if (NappaDialog->objectName().isEmpty())
            NappaDialog->setObjectName("NappaDialog");
        NappaDialog->setWindowModality(Qt::WindowModality::NonModal);
        NappaDialog->resize(778, 518);
        QSizePolicy sizePolicy(QSizePolicy::Policy::Fixed, QSizePolicy::Policy::Fixed);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(NappaDialog->sizePolicy().hasHeightForWidth());
        NappaDialog->setSizePolicy(sizePolicy);
        NappaDialog->setAcceptDrops(true);
        QIcon icon;
        icon.addFile(QString::fromUtf8(":/logo/nappa_icon.png"), QSize(), QIcon::Mode::Normal, QIcon::State::Off);
        icon.addFile(QString::fromUtf8(":/logo/nappa_icon.png"), QSize(), QIcon::Mode::Normal, QIcon::State::On);
        icon.addFile(QString::fromUtf8(":/logo/nappa_icon.png"), QSize(), QIcon::Mode::Disabled, QIcon::State::Off);
        icon.addFile(QString::fromUtf8(":/logo/nappa_icon.png"), QSize(), QIcon::Mode::Disabled, QIcon::State::On);
        icon.addFile(QString::fromUtf8(":/logo/nappa_icon.png"), QSize(), QIcon::Mode::Active, QIcon::State::Off);
        icon.addFile(QString::fromUtf8(":/logo/nappa_icon.png"), QSize(), QIcon::Mode::Active, QIcon::State::On);
        icon.addFile(QString::fromUtf8(":/logo/nappa_icon.png"), QSize(), QIcon::Mode::Selected, QIcon::State::Off);
        icon.addFile(QString::fromUtf8(":/logo/nappa_icon.png"), QSize(), QIcon::Mode::Selected, QIcon::State::On);
        NappaDialog->setWindowIcon(icon);
        gridLayout_5 = new QGridLayout(NappaDialog);
        gridLayout_5->setObjectName("gridLayout_5");
        informationGroupBox = new QGroupBox(NappaDialog);
        informationGroupBox->setObjectName("informationGroupBox");
        QSizePolicy sizePolicy1(QSizePolicy::Policy::MinimumExpanding, QSizePolicy::Policy::Preferred);
        sizePolicy1.setHorizontalStretch(0);
        sizePolicy1.setVerticalStretch(0);
        sizePolicy1.setHeightForWidth(informationGroupBox->sizePolicy().hasHeightForWidth());
        informationGroupBox->setSizePolicy(sizePolicy1);
        gridLayout_4 = new QGridLayout(informationGroupBox);
        gridLayout_4->setObjectName("gridLayout_4");
        label_4 = new QLabel(informationGroupBox);
        label_4->setObjectName("label_4");
        sizePolicy1.setHeightForWidth(label_4->sizePolicy().hasHeightForWidth());
        label_4->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(label_4, 0, 0, 1, 1);

        appVersionLabel = new QLabel(informationGroupBox);
        appVersionLabel->setObjectName("appVersionLabel");
        sizePolicy1.setHeightForWidth(appVersionLabel->sizePolicy().hasHeightForWidth());
        appVersionLabel->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(appVersionLabel, 1, 0, 1, 1);

        githubLabel = new QLabel(informationGroupBox);
        githubLabel->setObjectName("githubLabel");
        sizePolicy1.setHeightForWidth(githubLabel->sizePolicy().hasHeightForWidth());
        githubLabel->setSizePolicy(sizePolicy1);
        githubLabel->setOpenExternalLinks(true);

        gridLayout_4->addWidget(githubLabel, 1, 1, 1, 1);

        pluginVersionLabel = new QLabel(informationGroupBox);
        pluginVersionLabel->setObjectName("pluginVersionLabel");

        gridLayout_4->addWidget(pluginVersionLabel, 2, 0, 1, 1);


        gridLayout_5->addWidget(informationGroupBox, 0, 0, 1, 1);

        dataVisualizationGroupBox = new QGroupBox(NappaDialog);
        dataVisualizationGroupBox->setObjectName("dataVisualizationGroupBox");
        gridLayout = new QGridLayout(dataVisualizationGroupBox);
        gridLayout->setObjectName("gridLayout");
        tabWidget = new QTabWidget(dataVisualizationGroupBox);
        tabWidget->setObjectName("tabWidget");
        sizePolicy1.setHeightForWidth(tabWidget->sizePolicy().hasHeightForWidth());
        tabWidget->setSizePolicy(sizePolicy1);
        QPalette palette;
        QBrush brush(QColor(227, 227, 227, 255));
        brush.setStyle(Qt::SolidPattern);
        palette.setBrush(QPalette::Active, QPalette::Light, brush);
        palette.setBrush(QPalette::Active, QPalette::Base, brush);
        palette.setBrush(QPalette::Inactive, QPalette::Light, brush);
        palette.setBrush(QPalette::Inactive, QPalette::Base, brush);
        palette.setBrush(QPalette::Disabled, QPalette::Light, brush);
        tabWidget->setPalette(palette);
        tabWidget->setAutoFillBackground(false);
        tab = new QWidget();
        tab->setObjectName("tab");
        gridLayout_9 = new QGridLayout(tab);
        gridLayout_9->setObjectName("gridLayout_9");
        sleepMainGroupBox = new QGroupBox(tab);
        sleepMainGroupBox->setObjectName("sleepMainGroupBox");
        sizePolicy1.setHeightForWidth(sleepMainGroupBox->sizePolicy().hasHeightForWidth());
        sleepMainGroupBox->setSizePolicy(sizePolicy1);
        gridLayout_7 = new QGridLayout(sleepMainGroupBox);
        gridLayout_7->setObjectName("gridLayout_7");
        discreteHypnogramMainBox = new QRadioButton(sleepMainGroupBox);
        buttonGroup_2 = new QButtonGroup(NappaDialog);
        buttonGroup_2->setObjectName("buttonGroup_2");
        buttonGroup_2->addButton(discreteHypnogramMainBox);
        discreteHypnogramMainBox->setObjectName("discreteHypnogramMainBox");
        sizePolicy1.setHeightForWidth(discreteHypnogramMainBox->sizePolicy().hasHeightForWidth());
        discreteHypnogramMainBox->setSizePolicy(sizePolicy1);

        gridLayout_7->addWidget(discreteHypnogramMainBox, 0, 0, 1, 1);

        violinRadioButton = new QRadioButton(sleepMainGroupBox);
        buttonGroup = new QButtonGroup(NappaDialog);
        buttonGroup->setObjectName("buttonGroup");
        buttonGroup->addButton(violinRadioButton);
        violinRadioButton->setObjectName("violinRadioButton");
        sizePolicy1.setHeightForWidth(violinRadioButton->sizePolicy().hasHeightForWidth());
        violinRadioButton->setSizePolicy(sizePolicy1);

        gridLayout_7->addWidget(violinRadioButton, 0, 1, 1, 1);

        sdtMainBox = new QRadioButton(sleepMainGroupBox);
        buttonGroup_2->addButton(sdtMainBox);
        sdtMainBox->setObjectName("sdtMainBox");
        sizePolicy1.setHeightForWidth(sdtMainBox->sizePolicy().hasHeightForWidth());
        sdtMainBox->setSizePolicy(sizePolicy1);

        gridLayout_7->addWidget(sdtMainBox, 1, 0, 1, 1);

        barRadioButton = new QRadioButton(sleepMainGroupBox);
        buttonGroup->addButton(barRadioButton);
        barRadioButton->setObjectName("barRadioButton");
        sizePolicy1.setHeightForWidth(barRadioButton->sizePolicy().hasHeightForWidth());
        barRadioButton->setSizePolicy(sizePolicy1);

        gridLayout_7->addWidget(barRadioButton, 1, 1, 1, 1);

        sdtConfidenceMainBox = new QCheckBox(sleepMainGroupBox);
        sdtConfidenceMainBox->setObjectName("sdtConfidenceMainBox");
        sdtConfidenceMainBox->setEnabled(true);
        sizePolicy1.setHeightForWidth(sdtConfidenceMainBox->sizePolicy().hasHeightForWidth());
        sdtConfidenceMainBox->setSizePolicy(sizePolicy1);
        sdtConfidenceMainBox->setChecked(false);

        gridLayout_7->addWidget(sdtConfidenceMainBox, 2, 0, 1, 1);

        sleepStatisticsMainBox = new QCheckBox(sleepMainGroupBox);
        sleepStatisticsMainBox->setObjectName("sleepStatisticsMainBox");

        gridLayout_7->addWidget(sleepStatisticsMainBox, 2, 1, 1, 1);


        gridLayout_9->addWidget(sleepMainGroupBox, 0, 0, 1, 1);

        sensorDataMainGroupBox = new QGroupBox(tab);
        sensorDataMainGroupBox->setObjectName("sensorDataMainGroupBox");
        sizePolicy1.setHeightForWidth(sensorDataMainGroupBox->sizePolicy().hasHeightForWidth());
        sensorDataMainGroupBox->setSizePolicy(sizePolicy1);
        gridLayout_11 = new QGridLayout(sensorDataMainGroupBox);
        gridLayout_11->setObjectName("gridLayout_11");
        activityMainBox = new QCheckBox(sensorDataMainGroupBox);
        activityMainBox->setObjectName("activityMainBox");
        activityMainBox->setEnabled(true);
        sizePolicy1.setHeightForWidth(activityMainBox->sizePolicy().hasHeightForWidth());
        activityMainBox->setSizePolicy(sizePolicy1);
        activityMainBox->setChecked(false);

        gridLayout_11->addWidget(activityMainBox, 0, 0, 1, 1);

        respirationMainBox = new QCheckBox(sensorDataMainGroupBox);
        respirationMainBox->setObjectName("respirationMainBox");
        respirationMainBox->setEnabled(true);
        sizePolicy1.setHeightForWidth(respirationMainBox->sizePolicy().hasHeightForWidth());
        respirationMainBox->setSizePolicy(sizePolicy1);
        respirationMainBox->setChecked(false);

        gridLayout_11->addWidget(respirationMainBox, 1, 0, 1, 1);

        positionMainBox = new QCheckBox(sensorDataMainGroupBox);
        positionMainBox->setObjectName("positionMainBox");
        positionMainBox->setEnabled(true);
        sizePolicy1.setHeightForWidth(positionMainBox->sizePolicy().hasHeightForWidth());
        positionMainBox->setSizePolicy(sizePolicy1);
        positionMainBox->setChecked(false);

        gridLayout_11->addWidget(positionMainBox, 2, 0, 1, 1);


        gridLayout_9->addWidget(sensorDataMainGroupBox, 0, 1, 1, 1);

        tabWidget->addTab(tab, QString());
        tab_2 = new QWidget();
        tab_2->setObjectName("tab_2");
        gridLayout_10 = new QGridLayout(tab_2);
        gridLayout_10->setObjectName("gridLayout_10");
        sleepSubsqGroupBox = new QGroupBox(tab_2);
        sleepSubsqGroupBox->setObjectName("sleepSubsqGroupBox");
        gridLayout_3 = new QGridLayout(sleepSubsqGroupBox);
        gridLayout_3->setObjectName("gridLayout_3");
        discreteHypnogramSubsqBox = new QRadioButton(sleepSubsqGroupBox);
        discreteHypnogramSubsqBox->setObjectName("discreteHypnogramSubsqBox");

        gridLayout_3->addWidget(discreteHypnogramSubsqBox, 0, 0, 1, 1);

        donutSubsqBox = new QCheckBox(sleepSubsqGroupBox);
        donutSubsqBox->setObjectName("donutSubsqBox");

        gridLayout_3->addWidget(donutSubsqBox, 0, 1, 1, 1);

        sdtSubsqBox = new QRadioButton(sleepSubsqGroupBox);
        sdtSubsqBox->setObjectName("sdtSubsqBox");

        gridLayout_3->addWidget(sdtSubsqBox, 1, 0, 1, 1);

        sleepStatisticsSubsqBox = new QCheckBox(sleepSubsqGroupBox);
        sleepStatisticsSubsqBox->setObjectName("sleepStatisticsSubsqBox");

        gridLayout_3->addWidget(sleepStatisticsSubsqBox, 1, 1, 1, 1);

        sdtConfidenceSubsqBox = new QCheckBox(sleepSubsqGroupBox);
        sdtConfidenceSubsqBox->setObjectName("sdtConfidenceSubsqBox");
        sdtConfidenceSubsqBox->setEnabled(true);
        sdtConfidenceSubsqBox->setChecked(false);

        gridLayout_3->addWidget(sdtConfidenceSubsqBox, 2, 0, 1, 1);


        gridLayout_10->addWidget(sleepSubsqGroupBox, 0, 0, 1, 1);

        sensorDataSubsqGroupBox = new QGroupBox(tab_2);
        sensorDataSubsqGroupBox->setObjectName("sensorDataSubsqGroupBox");
        gridLayout_12 = new QGridLayout(sensorDataSubsqGroupBox);
        gridLayout_12->setObjectName("gridLayout_12");
        activitySubsqBox = new QCheckBox(sensorDataSubsqGroupBox);
        activitySubsqBox->setObjectName("activitySubsqBox");
        activitySubsqBox->setEnabled(true);
        activitySubsqBox->setChecked(false);

        gridLayout_12->addWidget(activitySubsqBox, 0, 0, 1, 1);

        respirationSubsqBox = new QCheckBox(sensorDataSubsqGroupBox);
        respirationSubsqBox->setObjectName("respirationSubsqBox");
        respirationSubsqBox->setEnabled(true);
        respirationSubsqBox->setChecked(false);

        gridLayout_12->addWidget(respirationSubsqBox, 1, 0, 1, 1);

        positionSubsqBox = new QCheckBox(sensorDataSubsqGroupBox);
        positionSubsqBox->setObjectName("positionSubsqBox");
        positionSubsqBox->setEnabled(true);
        positionSubsqBox->setChecked(false);

        gridLayout_12->addWidget(positionSubsqBox, 2, 0, 1, 1);


        gridLayout_10->addWidget(sensorDataSubsqGroupBox, 0, 1, 1, 1);

        tabWidget->addTab(tab_2, QString());

        gridLayout->addWidget(tabWidget, 0, 0, 1, 1);


        gridLayout_5->addWidget(dataVisualizationGroupBox, 0, 1, 1, 1);

        settingsGroupBox = new QGroupBox(NappaDialog);
        settingsGroupBox->setObjectName("settingsGroupBox");
        sizePolicy1.setHeightForWidth(settingsGroupBox->sizePolicy().hasHeightForWidth());
        settingsGroupBox->setSizePolicy(sizePolicy1);
        gridLayout_8 = new QGridLayout(settingsGroupBox);
        gridLayout_8->setObjectName("gridLayout_8");
        startTimeLabel = new QLabel(settingsGroupBox);
        startTimeLabel->setObjectName("startTimeLabel");
        sizePolicy1.setHeightForWidth(startTimeLabel->sizePolicy().hasHeightForWidth());
        startTimeLabel->setSizePolicy(sizePolicy1);

        gridLayout_8->addWidget(startTimeLabel, 0, 0, 1, 1);

        durationLabel = new QLabel(settingsGroupBox);
        durationLabel->setObjectName("durationLabel");
        sizePolicy1.setHeightForWidth(durationLabel->sizePolicy().hasHeightForWidth());
        durationLabel->setSizePolicy(sizePolicy1);

        gridLayout_8->addWidget(durationLabel, 1, 3, 1, 1);

        timeOffsetSpinBox = new QSpinBox(settingsGroupBox);
        timeOffsetSpinBox->setObjectName("timeOffsetSpinBox");
        sizePolicy1.setHeightForWidth(timeOffsetSpinBox->sizePolicy().hasHeightForWidth());
        timeOffsetSpinBox->setSizePolicy(sizePolicy1);
        timeOffsetSpinBox->setMinimum(-12);
        timeOffsetSpinBox->setMaximum(14);

        gridLayout_8->addWidget(timeOffsetSpinBox, 1, 2, 1, 1);

        selectPeriodsButton = new QPushButton(settingsGroupBox);
        selectPeriodsButton->setObjectName("selectPeriodsButton");
        sizePolicy1.setHeightForWidth(selectPeriodsButton->sizePolicy().hasHeightForWidth());
        selectPeriodsButton->setSizePolicy(sizePolicy1);

        gridLayout_8->addWidget(selectPeriodsButton, 1, 5, 1, 1);

        durationTitleLabel = new QLabel(settingsGroupBox);
        durationTitleLabel->setObjectName("durationTitleLabel");
        sizePolicy1.setHeightForWidth(durationTitleLabel->sizePolicy().hasHeightForWidth());
        durationTitleLabel->setSizePolicy(sizePolicy1);

        gridLayout_8->addWidget(durationTitleLabel, 0, 3, 1, 1);

        utcOffsetLabel = new QLabel(settingsGroupBox);
        utcOffsetLabel->setObjectName("utcOffsetLabel");
        sizePolicy1.setHeightForWidth(utcOffsetLabel->sizePolicy().hasHeightForWidth());
        utcOffsetLabel->setSizePolicy(sizePolicy1);

        gridLayout_8->addWidget(utcOffsetLabel, 0, 2, 1, 1);

        endTimeLabel = new QLabel(settingsGroupBox);
        endTimeLabel->setObjectName("endTimeLabel");
        sizePolicy1.setHeightForWidth(endTimeLabel->sizePolicy().hasHeightForWidth());
        endTimeLabel->setSizePolicy(sizePolicy1);

        gridLayout_8->addWidget(endTimeLabel, 0, 1, 1, 1);

        advancedSettingsButton = new QPushButton(settingsGroupBox);
        advancedSettingsButton->setObjectName("advancedSettingsButton");
        sizePolicy1.setHeightForWidth(advancedSettingsButton->sizePolicy().hasHeightForWidth());
        advancedSettingsButton->setSizePolicy(sizePolicy1);

        gridLayout_8->addWidget(advancedSettingsButton, 0, 5, 1, 1);

        endTime = new QDateTimeEdit(settingsGroupBox);
        endTime->setObjectName("endTime");
        endTime->setEnabled(false);
        sizePolicy1.setHeightForWidth(endTime->sizePolicy().hasHeightForWidth());
        endTime->setSizePolicy(sizePolicy1);
        endTime->setDateTime(QDateTime(QDate(2024, 1, 2), QTime(9, 0, 0)));

        gridLayout_8->addWidget(endTime, 1, 1, 1, 1);

        startTime = new QDateTimeEdit(settingsGroupBox);
        startTime->setObjectName("startTime");
        startTime->setEnabled(false);
        sizePolicy1.setHeightForWidth(startTime->sizePolicy().hasHeightForWidth());
        startTime->setSizePolicy(sizePolicy1);
        startTime->setDateTime(QDateTime(QDate(2024, 1, 1), QTime(21, 0, 0)));
        startTime->setTime(QTime(21, 0, 0));
        startTime->setMinimumDateTime(QDateTime(QDate(1752, 9, 14), QTime(0, 0, 2)));

        gridLayout_8->addWidget(startTime, 1, 0, 1, 1);

        sleepPeriodsTitleLabel = new QLabel(settingsGroupBox);
        sleepPeriodsTitleLabel->setObjectName("sleepPeriodsTitleLabel");
        sizePolicy1.setHeightForWidth(sleepPeriodsTitleLabel->sizePolicy().hasHeightForWidth());
        sleepPeriodsTitleLabel->setSizePolicy(sizePolicy1);

        gridLayout_8->addWidget(sleepPeriodsTitleLabel, 0, 4, 1, 1);

        sleepPeriodsLabel = new QLabel(settingsGroupBox);
        sleepPeriodsLabel->setObjectName("sleepPeriodsLabel");
        sizePolicy1.setHeightForWidth(sleepPeriodsLabel->sizePolicy().hasHeightForWidth());
        sleepPeriodsLabel->setSizePolicy(sizePolicy1);

        gridLayout_8->addWidget(sleepPeriodsLabel, 1, 4, 1, 1);


        gridLayout_5->addWidget(settingsGroupBox, 1, 0, 1, 2);

        analysisGroupBox = new QGroupBox(NappaDialog);
        analysisGroupBox->setObjectName("analysisGroupBox");
        sizePolicy1.setHeightForWidth(analysisGroupBox->sizePolicy().hasHeightForWidth());
        analysisGroupBox->setSizePolicy(sizePolicy1);
        horizontalLayout = new QHBoxLayout(analysisGroupBox);
        horizontalLayout->setObjectName("horizontalLayout");
        statusLabel = new QLabel(analysisGroupBox);
        statusLabel->setObjectName("statusLabel");
        sizePolicy1.setHeightForWidth(statusLabel->sizePolicy().hasHeightForWidth());
        statusLabel->setSizePolicy(sizePolicy1);

        horizontalLayout->addWidget(statusLabel);

        analyzeButton = new QPushButton(analysisGroupBox);
        analyzeButton->setObjectName("analyzeButton");
        analyzeButton->setEnabled(true);
        sizePolicy1.setHeightForWidth(analyzeButton->sizePolicy().hasHeightForWidth());
        analyzeButton->setSizePolicy(sizePolicy1);

        horizontalLayout->addWidget(analyzeButton);


        gridLayout_5->addWidget(analysisGroupBox, 3, 0, 1, 2);

        dataGroupBox = new QGroupBox(NappaDialog);
        dataGroupBox->setObjectName("dataGroupBox");
        sizePolicy1.setHeightForWidth(dataGroupBox->sizePolicy().hasHeightForWidth());
        dataGroupBox->setSizePolicy(sizePolicy1);
        gridLayout_2 = new QGridLayout(dataGroupBox);
        gridLayout_2->setObjectName("gridLayout_2");
        inputFile = new QLineEdit(dataGroupBox);
        inputFile->setObjectName("inputFile");
        sizePolicy1.setHeightForWidth(inputFile->sizePolicy().hasHeightForWidth());
        inputFile->setSizePolicy(sizePolicy1);

        gridLayout_2->addWidget(inputFile, 0, 1, 1, 1);

        outputFileLabel = new QLabel(dataGroupBox);
        outputFileLabel->setObjectName("outputFileLabel");
        QSizePolicy sizePolicy2(QSizePolicy::Policy::Fixed, QSizePolicy::Policy::Preferred);
        sizePolicy2.setHorizontalStretch(0);
        sizePolicy2.setVerticalStretch(0);
        sizePolicy2.setHeightForWidth(outputFileLabel->sizePolicy().hasHeightForWidth());
        outputFileLabel->setSizePolicy(sizePolicy2);

        gridLayout_2->addWidget(outputFileLabel, 1, 0, 1, 1);

        inputFileLabel = new QLabel(dataGroupBox);
        inputFileLabel->setObjectName("inputFileLabel");
        sizePolicy2.setHeightForWidth(inputFileLabel->sizePolicy().hasHeightForWidth());
        inputFileLabel->setSizePolicy(sizePolicy2);

        gridLayout_2->addWidget(inputFileLabel, 0, 0, 1, 1);

        outputFile = new QLineEdit(dataGroupBox);
        outputFile->setObjectName("outputFile");
        sizePolicy1.setHeightForWidth(outputFile->sizePolicy().hasHeightForWidth());
        outputFile->setSizePolicy(sizePolicy1);

        gridLayout_2->addWidget(outputFile, 1, 1, 1, 1);

        browseInputButton = new QPushButton(dataGroupBox);
        browseInputButton->setObjectName("browseInputButton");
        sizePolicy2.setHeightForWidth(browseInputButton->sizePolicy().hasHeightForWidth());
        browseInputButton->setSizePolicy(sizePolicy2);

        gridLayout_2->addWidget(browseInputButton, 0, 2, 1, 1);

        browseOutputButton = new QPushButton(dataGroupBox);
        browseOutputButton->setObjectName("browseOutputButton");
        sizePolicy2.setHeightForWidth(browseOutputButton->sizePolicy().hasHeightForWidth());
        browseOutputButton->setSizePolicy(sizePolicy2);

        gridLayout_2->addWidget(browseOutputButton, 1, 2, 1, 1);


        gridLayout_5->addWidget(dataGroupBox, 2, 0, 1, 2);


        retranslateUi(NappaDialog);

        tabWidget->setCurrentIndex(1);


        QMetaObject::connectSlotsByName(NappaDialog);
    } // setupUi

    void retranslateUi(QDialog* NappaDialog)
    {
        NappaDialog->setWindowTitle(QCoreApplication::translate("NappaDialog", "NAPPA Infant Sleep Analyzer", nullptr));
        informationGroupBox->setTitle(QCoreApplication::translate("NappaDialog", "Information", nullptr));
        label_4->setText(QCoreApplication::translate("NappaDialog", "<html><head/><body><p><img src=\":/logo/baba-logo.png\"/></p></body></html>", nullptr));
        appVersionLabel->setText(QCoreApplication::translate("NappaDialog", "App version: x.x", nullptr));
#if QT_CONFIG(tooltip)
        githubLabel->setToolTip(QCoreApplication::translate("NappaDialog", "Please visit the github repository! Propose bug fixes/new features/improvements.", nullptr));
#endif // QT_CONFIG(tooltip)
        githubLabel->setText(QCoreApplication::translate("NappaDialog", "<html><head/><body><p><a href=\"https://github.com/matiashaggman/NAPPA-ISA\"><span style=\" text-decoration: underline; color:#007af4;\">Github</span></a></p></body></html>", nullptr));
#if QT_CONFIG(tooltip)
        pluginVersionLabel->setToolTip(QCoreApplication::translate("NappaDialog", "NAPPA plugin allows real-time feature updates for the application.", nullptr));
#endif // QT_CONFIG(tooltip)
        pluginVersionLabel->setText(QCoreApplication::translate("NappaDialog", "Plugin version: x.x", nullptr));
        dataVisualizationGroupBox->setTitle(QCoreApplication::translate("NappaDialog", "Data visualization", nullptr));
        sleepMainGroupBox->setTitle(QCoreApplication::translate("NappaDialog", "Sleep", nullptr));
        discreteHypnogramMainBox->setText(QCoreApplication::translate("NappaDialog", "Discrete hypnogram", nullptr));
        violinRadioButton->setText(QCoreApplication::translate("NappaDialog", "Violin plot", nullptr));
        sdtMainBox->setText(QCoreApplication::translate("NappaDialog", "Sleep Depth Trend", nullptr));
        barRadioButton->setText(QCoreApplication::translate("NappaDialog", "Bar plot", nullptr));
        sdtConfidenceMainBox->setText(QCoreApplication::translate("NappaDialog", "Sleep Depth Trend\n"
            "Confidence Interval", nullptr));
        sleepStatisticsMainBox->setText(QCoreApplication::translate("NappaDialog", "Sleep statistics\n"
            "(text)", nullptr));
        sensorDataMainGroupBox->setTitle(QCoreApplication::translate("NappaDialog", "Sensor data", nullptr));
        activityMainBox->setText(QCoreApplication::translate("NappaDialog", "Activity", nullptr));
        respirationMainBox->setText(QCoreApplication::translate("NappaDialog", "Respiration rate", nullptr));
        positionMainBox->setText(QCoreApplication::translate("NappaDialog", "Position", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(tab), QCoreApplication::translate("NappaDialog", "Main page", nullptr));
        sleepSubsqGroupBox->setTitle(QCoreApplication::translate("NappaDialog", "Sleep", nullptr));
        discreteHypnogramSubsqBox->setText(QCoreApplication::translate("NappaDialog", "Discrete hypnogram", nullptr));
        donutSubsqBox->setText(QCoreApplication::translate("NappaDialog", "Donut plot", nullptr));
        sdtSubsqBox->setText(QCoreApplication::translate("NappaDialog", "Sleep Depth Trend", nullptr));
        sleepStatisticsSubsqBox->setText(QCoreApplication::translate("NappaDialog", "Sleep statistics\n"
            "(text)", nullptr));
        sdtConfidenceSubsqBox->setText(QCoreApplication::translate("NappaDialog", "Sleep Depth Trend\n"
            "Confidence Interval", nullptr));
        sensorDataSubsqGroupBox->setTitle(QCoreApplication::translate("NappaDialog", "Sensor data", nullptr));
        activitySubsqBox->setText(QCoreApplication::translate("NappaDialog", "Activity", nullptr));
        respirationSubsqBox->setText(QCoreApplication::translate("NappaDialog", "Respiration rate", nullptr));
        positionSubsqBox->setText(QCoreApplication::translate("NappaDialog", "Position", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(tab_2), QCoreApplication::translate("NappaDialog", "Subsequent pages", nullptr));
        settingsGroupBox->setTitle(QCoreApplication::translate("NappaDialog", "Settings", nullptr));
        startTimeLabel->setText(QCoreApplication::translate("NappaDialog", "Start time", nullptr));
        durationLabel->setText(QCoreApplication::translate("NappaDialog", "0 h", nullptr));
        selectPeriodsButton->setText(QCoreApplication::translate("NappaDialog", "Enter sleep periods", nullptr));
        durationTitleLabel->setText(QCoreApplication::translate("NappaDialog", "Duration", nullptr));
        utcOffsetLabel->setText(QCoreApplication::translate("NappaDialog", "UTC offset", nullptr));
        endTimeLabel->setText(QCoreApplication::translate("NappaDialog", "End time", nullptr));
        advancedSettingsButton->setText(QCoreApplication::translate("NappaDialog", "Advanced settings", nullptr));
        endTime->setDisplayFormat(QCoreApplication::translate("NappaDialog", "dd/MM/yyyy HH:mm", nullptr));
        startTime->setDisplayFormat(QCoreApplication::translate("NappaDialog", "dd/MM/yyyy HH:mm", nullptr));
        sleepPeriodsTitleLabel->setText(QCoreApplication::translate("NappaDialog", "Sleep periods", nullptr));
#if QT_CONFIG(tooltip)
        sleepPeriodsLabel->setToolTip(QCoreApplication::translate("NappaDialog", "Number of automatically inferred sleeping periods.", nullptr));
#endif // QT_CONFIG(tooltip)
        sleepPeriodsLabel->setText(QCoreApplication::translate("NappaDialog", "0", nullptr));
        analysisGroupBox->setTitle(QCoreApplication::translate("NappaDialog", "Analysis", nullptr));
        statusLabel->setText(QCoreApplication::translate("NappaDialog", "Status: awaiting user input (drop zip file anywhere)", nullptr));
        analyzeButton->setText(QCoreApplication::translate("NappaDialog", "Analyze", nullptr));
        dataGroupBox->setTitle(QCoreApplication::translate("NappaDialog", "Data", nullptr));
#if QT_CONFIG(tooltip)
        inputFile->setToolTip(QCoreApplication::translate("NappaDialog", "<html><head/><body><p>Input file (.zip) containing the accelerometer and gyroscope from the sleep pants' sensor.</p></body></html>", nullptr));
#endif // QT_CONFIG(tooltip)
        outputFileLabel->setText(QCoreApplication::translate("NappaDialog", "Output file:", nullptr));
        inputFileLabel->setText(QCoreApplication::translate("NappaDialog", "Input file:", nullptr));
#if QT_CONFIG(tooltip)
        outputFile->setToolTip(QCoreApplication::translate("NappaDialog", "<html><head/><body><p>Output file (.zip) name. </p></body></html>", nullptr));
#endif // QT_CONFIG(tooltip)
        browseInputButton->setText(QCoreApplication::translate("NappaDialog", "Browse", nullptr));
        browseOutputButton->setText(QCoreApplication::translate("NappaDialog", "Browse", nullptr));
    } // retranslateUi

};

namespace Ui {
    class NappaDialog : public Ui_NappaDialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // MAIN_WINDOWJQKIYT_H
