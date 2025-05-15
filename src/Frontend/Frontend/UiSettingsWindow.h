/********************************************************************************
** Form generated from reading UI file 'settings_windowyXDvYY.ui'
**
** Created by: Qt User Interface Compiler version 6.7.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef SETTINGS_WINDOWYXDVYY_H
#define SETTINGS_WINDOWYXDVYY_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QCheckBox>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QDialog>
#include <QtWidgets/QDoubleSpinBox>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QRadioButton>

QT_BEGIN_NAMESPACE

class Ui_Settings
{
public:
    QGridLayout* gridLayout_5;
    QGroupBox* reportTypeGroupBox;
    QGridLayout* gridLayout_3;
    QRadioButton* singlePageButton;
    QRadioButton* multipageButton;
    QGroupBox* plotDetailsGroupBox;
    QGridLayout* gridLayout_4;
    QLabel* label_15;
    QCheckBox* filterBox;
    QLabel* label_9;
    QDoubleSpinBox* filterWindowSpinBox;
    QLabel* windowSizeLabel;
    QCheckBox* filterNonwearBox;
    QComboBox* dateStyleBox;
    QLabel* label_16;
    QCheckBox* logScaleBox;
    QDoubleSpinBox* reportQualityBox;
    QDoubleSpinBox* xTicksBox;
    QGroupBox* classifierInputGroupBox;
    QGridLayout* gridLayout_2;
    QRadioButton* fullFeaturesButton;
    QRadioButton* accelerometerOnlyButton;
    QGroupBox* outputFilesGroupBox;
    QGridLayout* gridLayout;
    QCheckBox* pdfOutputBox;
    QCheckBox* figuresOutputBox;
    QCheckBox* csvOutputBox;
    QGroupBox* pageGenerationGroupBox;
    QGroupBox* extensionBox;
    QHBoxLayout* horizontalLayout;
    QRadioButton* pageGenerationAutomaticButton;
    QRadioButton* pageGenerationManualButton;
    QPushButton* saveButton;

    void setupUi(QDialog* Settings)
    {
        if (Settings->objectName().isEmpty())
            Settings->setObjectName("Settings");
        Settings->resize(521, 370);
        QSizePolicy sizePolicy(QSizePolicy::Policy::Fixed, QSizePolicy::Policy::Fixed);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(Settings->sizePolicy().hasHeightForWidth());
        Settings->setSizePolicy(sizePolicy);
        gridLayout_5 = new QGridLayout(Settings);
        gridLayout_5->setObjectName("gridLayout_5");
        reportTypeGroupBox = new QGroupBox(Settings);
        reportTypeGroupBox->setObjectName("reportTypeGroupBox");
        QSizePolicy sizePolicy1(QSizePolicy::Policy::MinimumExpanding, QSizePolicy::Policy::Preferred);
        sizePolicy1.setHorizontalStretch(0);
        sizePolicy1.setVerticalStretch(0);
        sizePolicy1.setHeightForWidth(reportTypeGroupBox->sizePolicy().hasHeightForWidth());
        reportTypeGroupBox->setSizePolicy(sizePolicy1);
        gridLayout_3 = new QGridLayout(reportTypeGroupBox);
        gridLayout_3->setObjectName("gridLayout_3");
        singlePageButton = new QRadioButton(reportTypeGroupBox);
        singlePageButton->setObjectName("singlePageButton");
        sizePolicy1.setHeightForWidth(singlePageButton->sizePolicy().hasHeightForWidth());
        singlePageButton->setSizePolicy(sizePolicy1);

        gridLayout_3->addWidget(singlePageButton, 0, 0, 1, 1);

        multipageButton = new QRadioButton(reportTypeGroupBox);
        multipageButton->setObjectName("multipageButton");
        sizePolicy1.setHeightForWidth(multipageButton->sizePolicy().hasHeightForWidth());
        multipageButton->setSizePolicy(sizePolicy1);

        gridLayout_3->addWidget(multipageButton, 1, 0, 1, 1);


        gridLayout_5->addWidget(reportTypeGroupBox, 2, 0, 2, 1);

        plotDetailsGroupBox = new QGroupBox(Settings);
        plotDetailsGroupBox->setObjectName("plotDetailsGroupBox");
        sizePolicy1.setHeightForWidth(plotDetailsGroupBox->sizePolicy().hasHeightForWidth());
        plotDetailsGroupBox->setSizePolicy(sizePolicy1);
        gridLayout_4 = new QGridLayout(plotDetailsGroupBox);
        gridLayout_4->setObjectName("gridLayout_4");
        label_15 = new QLabel(plotDetailsGroupBox);
        label_15->setObjectName("label_15");
        sizePolicy1.setHeightForWidth(label_15->sizePolicy().hasHeightForWidth());
        label_15->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(label_15, 1, 0, 2, 2);

        filterBox = new QCheckBox(plotDetailsGroupBox);
        filterBox->setObjectName("filterBox");
        sizePolicy1.setHeightForWidth(filterBox->sizePolicy().hasHeightForWidth());
        filterBox->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(filterBox, 2, 3, 1, 2);

        label_9 = new QLabel(plotDetailsGroupBox);
        label_9->setObjectName("label_9");
        sizePolicy1.setHeightForWidth(label_9->sizePolicy().hasHeightForWidth());
        label_9->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(label_9, 0, 0, 1, 2);

        filterWindowSpinBox = new QDoubleSpinBox(plotDetailsGroupBox);
        filterWindowSpinBox->setObjectName("filterWindowSpinBox");
        filterWindowSpinBox->setEnabled(true);
        sizePolicy1.setHeightForWidth(filterWindowSpinBox->sizePolicy().hasHeightForWidth());
        filterWindowSpinBox->setSizePolicy(sizePolicy1);
        filterWindowSpinBox->setDecimals(0);
        filterWindowSpinBox->setMinimum(3.000000000000000);
        filterWindowSpinBox->setMaximum(101.000000000000000);
        filterWindowSpinBox->setSingleStep(1.000000000000000);
        filterWindowSpinBox->setValue(3.000000000000000);

        gridLayout_4->addWidget(filterWindowSpinBox, 3, 4, 1, 1);

        windowSizeLabel = new QLabel(plotDetailsGroupBox);
        windowSizeLabel->setObjectName("windowSizeLabel");
        windowSizeLabel->setEnabled(true);
        sizePolicy1.setHeightForWidth(windowSizeLabel->sizePolicy().hasHeightForWidth());
        windowSizeLabel->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(windowSizeLabel, 3, 3, 1, 1);

        filterNonwearBox = new QCheckBox(plotDetailsGroupBox);
        filterNonwearBox->setObjectName("filterNonwearBox");
        sizePolicy1.setHeightForWidth(filterNonwearBox->sizePolicy().hasHeightForWidth());
        filterNonwearBox->setSizePolicy(sizePolicy1);
        filterNonwearBox->setChecked(false);

        gridLayout_4->addWidget(filterNonwearBox, 0, 3, 1, 2);

        dateStyleBox = new QComboBox(plotDetailsGroupBox);
        dateStyleBox->addItem(QString());
        dateStyleBox->addItem(QString());
        dateStyleBox->addItem(QString());
        dateStyleBox->addItem(QString());
        dateStyleBox->addItem(QString());
        dateStyleBox->setObjectName("dateStyleBox");
        sizePolicy1.setHeightForWidth(dateStyleBox->sizePolicy().hasHeightForWidth());
        dateStyleBox->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(dateStyleBox, 3, 1, 1, 2);

        label_16 = new QLabel(plotDetailsGroupBox);
        label_16->setObjectName("label_16");
        sizePolicy1.setHeightForWidth(label_16->sizePolicy().hasHeightForWidth());
        label_16->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(label_16, 3, 0, 1, 1);

        logScaleBox = new QCheckBox(plotDetailsGroupBox);
        logScaleBox->setObjectName("logScaleBox");
        sizePolicy1.setHeightForWidth(logScaleBox->sizePolicy().hasHeightForWidth());
        logScaleBox->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(logScaleBox, 1, 3, 1, 2);

        reportQualityBox = new QDoubleSpinBox(plotDetailsGroupBox);
        reportQualityBox->setObjectName("reportQualityBox");
        reportQualityBox->setEnabled(true);
        sizePolicy1.setHeightForWidth(reportQualityBox->sizePolicy().hasHeightForWidth());
        reportQualityBox->setSizePolicy(sizePolicy1);
        reportQualityBox->setDecimals(0);
        reportQualityBox->setMinimum(10.000000000000000);
        reportQualityBox->setMaximum(500.000000000000000);
        reportQualityBox->setSingleStep(10.000000000000000);
        reportQualityBox->setValue(100.000000000000000);

        gridLayout_4->addWidget(reportQualityBox, 0, 2, 1, 1);

        xTicksBox = new QDoubleSpinBox(plotDetailsGroupBox);
        xTicksBox->setObjectName("xTicksBox");
        xTicksBox->setEnabled(true);
        sizePolicy1.setHeightForWidth(xTicksBox->sizePolicy().hasHeightForWidth());
        xTicksBox->setSizePolicy(sizePolicy1);
        xTicksBox->setDecimals(0);
        xTicksBox->setMinimum(2.000000000000000);
        xTicksBox->setMaximum(100.000000000000000);
        xTicksBox->setSingleStep(1.000000000000000);
        xTicksBox->setValue(8.000000000000000);

        gridLayout_4->addWidget(xTicksBox, 1, 2, 2, 1);


        gridLayout_5->addWidget(plotDetailsGroupBox, 0, 0, 1, 4);

        classifierInputGroupBox = new QGroupBox(Settings);
        classifierInputGroupBox->setObjectName("classifierInputGroupBox");
        sizePolicy1.setHeightForWidth(classifierInputGroupBox->sizePolicy().hasHeightForWidth());
        classifierInputGroupBox->setSizePolicy(sizePolicy1);
        gridLayout_2 = new QGridLayout(classifierInputGroupBox);
        gridLayout_2->setObjectName("gridLayout_2");
        fullFeaturesButton = new QRadioButton(classifierInputGroupBox);
        fullFeaturesButton->setObjectName("fullFeaturesButton");
        sizePolicy1.setHeightForWidth(fullFeaturesButton->sizePolicy().hasHeightForWidth());
        fullFeaturesButton->setSizePolicy(sizePolicy1);

        gridLayout_2->addWidget(fullFeaturesButton, 0, 0, 1, 1);

        accelerometerOnlyButton = new QRadioButton(classifierInputGroupBox);
        accelerometerOnlyButton->setObjectName("accelerometerOnlyButton");
        sizePolicy1.setHeightForWidth(accelerometerOnlyButton->sizePolicy().hasHeightForWidth());
        accelerometerOnlyButton->setSizePolicy(sizePolicy1);

        gridLayout_2->addWidget(accelerometerOnlyButton, 1, 0, 1, 1);


        gridLayout_5->addWidget(classifierInputGroupBox, 1, 0, 1, 1);

        outputFilesGroupBox = new QGroupBox(Settings);
        outputFilesGroupBox->setObjectName("outputFilesGroupBox");
        sizePolicy1.setHeightForWidth(outputFilesGroupBox->sizePolicy().hasHeightForWidth());
        outputFilesGroupBox->setSizePolicy(sizePolicy1);
        gridLayout = new QGridLayout(outputFilesGroupBox);
        gridLayout->setObjectName("gridLayout");
        pdfOutputBox = new QCheckBox(outputFilesGroupBox);
        pdfOutputBox->setObjectName("pdfOutputBox");
        sizePolicy1.setHeightForWidth(pdfOutputBox->sizePolicy().hasHeightForWidth());
        pdfOutputBox->setSizePolicy(sizePolicy1);

        gridLayout->addWidget(pdfOutputBox, 0, 0, 1, 1);

        figuresOutputBox = new QCheckBox(outputFilesGroupBox);
        figuresOutputBox->setObjectName("figuresOutputBox");
        sizePolicy1.setHeightForWidth(figuresOutputBox->sizePolicy().hasHeightForWidth());
        figuresOutputBox->setSizePolicy(sizePolicy1);

        gridLayout->addWidget(figuresOutputBox, 3, 0, 1, 1);

        csvOutputBox = new QCheckBox(outputFilesGroupBox);
        csvOutputBox->setObjectName("csvOutputBox");
        sizePolicy1.setHeightForWidth(csvOutputBox->sizePolicy().hasHeightForWidth());
        csvOutputBox->setSizePolicy(sizePolicy1);

        gridLayout->addWidget(csvOutputBox, 2, 0, 1, 1);


        gridLayout_5->addWidget(outputFilesGroupBox, 1, 1, 1, 1);

        pageGenerationGroupBox = new QGroupBox(Settings);
        pageGenerationGroupBox->setObjectName("pageGenerationGroupBox");
        sizePolicy1.setHeightForWidth(pageGenerationGroupBox->sizePolicy().hasHeightForWidth());
        pageGenerationGroupBox->setSizePolicy(sizePolicy1);
        horizontalLayout = new QHBoxLayout(pageGenerationGroupBox);
        horizontalLayout->setObjectName("horizontalLayout");
        pageGenerationAutomaticButton = new QRadioButton(pageGenerationGroupBox);
        pageGenerationAutomaticButton->setObjectName("pageGenerationAutomaticButton");
        sizePolicy1.setHeightForWidth(pageGenerationAutomaticButton->sizePolicy().hasHeightForWidth());
        pageGenerationAutomaticButton->setSizePolicy(sizePolicy1);

        horizontalLayout->addWidget(pageGenerationAutomaticButton);

        pageGenerationManualButton = new QRadioButton(pageGenerationGroupBox);
        pageGenerationManualButton->setObjectName("pageGenerationManualButton");
        sizePolicy1.setHeightForWidth(pageGenerationManualButton->sizePolicy().hasHeightForWidth());
        pageGenerationManualButton->setSizePolicy(sizePolicy1);

        horizontalLayout->addWidget(pageGenerationManualButton);


        gridLayout_5->addWidget(pageGenerationGroupBox, 2, 1, 1, 1);

        saveButton = new QPushButton(Settings);
        saveButton->setObjectName("saveButton");

        gridLayout_5->addWidget(saveButton, 3, 1, 1, 1);


        retranslateUi(Settings);

        QMetaObject::connectSlotsByName(Settings);
    } // setupUi

    void retranslateUi(QDialog* Settings)
    {
        Settings->setWindowTitle(QCoreApplication::translate("Settings", "Settings", nullptr));
        reportTypeGroupBox->setTitle(QCoreApplication::translate("Settings", "Report type", nullptr));
#if QT_CONFIG(tooltip)
        singlePageButton->setToolTip(QCoreApplication::translate("Settings", "Print only the summary page. Suitable for single night recordings.", nullptr));
#endif // QT_CONFIG(tooltip)
        singlePageButton->setText(QCoreApplication::translate("Settings", "Single page (summary of all data)", nullptr));
#if QT_CONFIG(tooltip)
        multipageButton->setToolTip(QCoreApplication::translate("Settings", "Print a summary page summarizing the whole recording and individual subsequent pages for each period of sleep.", nullptr));
#endif // QT_CONFIG(tooltip)
        multipageButton->setText(QCoreApplication::translate("Settings", "Multipage (summary + individual sleep periods)", nullptr));
        plotDetailsGroupBox->setTitle(QCoreApplication::translate("Settings", "Plot details", nullptr));
        label_15->setText(QCoreApplication::translate("Settings", "Number of  X-axis ticks:", nullptr));
#if QT_CONFIG(tooltip)
        filterBox->setToolTip(QCoreApplication::translate("Settings", "<html><head/><body><p>Select whether to use median filtering for smoothing out the sensor signals and sleep depth trend.</p></body></html>", nullptr));
#endif // QT_CONFIG(tooltip)
        filterBox->setText(QCoreApplication::translate("Settings", "Median filter (all data)", nullptr));
        label_9->setText(QCoreApplication::translate("Settings", "Plot quality (DPI):", nullptr));
#if QT_CONFIG(tooltip)
        filterWindowSpinBox->setToolTip(QCoreApplication::translate("Settings", "<html><head/><body><p>Defines the window size for the median filter for signal smoothing. Default = 3.</p></body></html>", nullptr));
#endif // QT_CONFIG(tooltip)
        windowSizeLabel->setText(QCoreApplication::translate("Settings", "Median filter window size:\n"
            " (minutes)", nullptr));
#if QT_CONFIG(tooltip)
        filterNonwearBox->setToolTip(QCoreApplication::translate("Settings", "<html><head/><body><p>Gray-out periods of nonwear (sensor not worn) in the plots.</p></body></html>", nullptr));
#endif // QT_CONFIG(tooltip)
        filterNonwearBox->setText(QCoreApplication::translate("Settings", "Filter-out nonwear", nullptr));
        dateStyleBox->setItemText(0, QCoreApplication::translate("Settings", "dd.mm. hh", nullptr));
        dateStyleBox->setItemText(1, QCoreApplication::translate("Settings", "dd/mm hh", nullptr));
        dateStyleBox->setItemText(2, QCoreApplication::translate("Settings", "dd.mm.yyyy hh", nullptr));
        dateStyleBox->setItemText(3, QCoreApplication::translate("Settings", "dd/mm/yyyy hh", nullptr));
        dateStyleBox->setItemText(4, QCoreApplication::translate("Settings", "hh:mm", nullptr));

        label_16->setText(QCoreApplication::translate("Settings", "Date style:", nullptr));
#if QT_CONFIG(tooltip)
        logScaleBox->setToolTip(QCoreApplication::translate("Settings", "Use logarithmic scale on the y-axis of the activity plot.", nullptr));
#endif // QT_CONFIG(tooltip)
        logScaleBox->setText(QCoreApplication::translate("Settings", "Activity feature log scale", nullptr));
#if QT_CONFIG(tooltip)
        reportQualityBox->setToolTip(QCoreApplication::translate("Settings", "<html><head/><body><p>Defines the DPI (Dots Per Inch) for the report grapics. Higher DPI = longer report compile time.</p></body></html>", nullptr));
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        xTicksBox->setToolTip(QCoreApplication::translate("Settings", "<html><head/><body><p>Maximum number of ticks on the x-axis of the main figure.</p></body></html>", nullptr));
#endif // QT_CONFIG(tooltip)
        classifierInputGroupBox->setTitle(QCoreApplication::translate("Settings", "Classifier input", nullptr));
#if QT_CONFIG(tooltip)
        fullFeaturesButton->setToolTip(QCoreApplication::translate("Settings", "Use all five standard features for sleep staging.", nullptr));
#endif // QT_CONFIG(tooltip)
        fullFeaturesButton->setText(QCoreApplication::translate("Settings", "All standard features", nullptr));
#if QT_CONFIG(tooltip)
        accelerometerOnlyButton->setToolTip(QCoreApplication::translate("Settings", "Use only accelerometer 'activity' feature for sleep staging.", nullptr));
#endif // QT_CONFIG(tooltip)
        accelerometerOnlyButton->setText(QCoreApplication::translate("Settings", "Activity feature only (accelerometer)", nullptr));
        outputFilesGroupBox->setTitle(QCoreApplication::translate("Settings", "Output files", nullptr));
#if QT_CONFIG(tooltip)
        pdfOutputBox->setToolTip(QCoreApplication::translate("Settings", "Generate a pdf report of the analysis.", nullptr));
#endif // QT_CONFIG(tooltip)
        pdfOutputBox->setText(QCoreApplication::translate("Settings", "Report (.pdf)", nullptr));
#if QT_CONFIG(tooltip)
        figuresOutputBox->setToolTip(QCoreApplication::translate("Settings", "<html><head/><body><p>Export all the generated plots as .png files.</p></body></html>", nullptr));
#endif // QT_CONFIG(tooltip)
        figuresOutputBox->setText(QCoreApplication::translate("Settings", "Figures (.png)", nullptr));
#if QT_CONFIG(tooltip)
        csvOutputBox->setToolTip(QCoreApplication::translate("Settings", "Generate a .csv file containing the classifier output.", nullptr));
#endif // QT_CONFIG(tooltip)
        csvOutputBox->setText(QCoreApplication::translate("Settings", "Classifier output (.csv)", nullptr));
        pageGenerationGroupBox->setTitle(QCoreApplication::translate("Settings", "Page generation (sleep periods)", nullptr));
#if QT_CONFIG(tooltip)
        pageGenerationAutomaticButton->setToolTip(QCoreApplication::translate("Settings", "Automatically infer sleep periods.", nullptr));
#endif // QT_CONFIG(tooltip)
        pageGenerationAutomaticButton->setText(QCoreApplication::translate("Settings", "Automatic", nullptr));
#if QT_CONFIG(tooltip)
        pageGenerationManualButton->setToolTip(QCoreApplication::translate("Settings", "Enter sleep periods manually.", nullptr));
#endif // QT_CONFIG(tooltip)
        pageGenerationManualButton->setText(QCoreApplication::translate("Settings", "Manual", nullptr));
        saveButton->setText(QCoreApplication::translate("Settings", "Save", nullptr));
    } // retranslateUi

};

namespace Ui {
    class Settings : public Ui_Settings {};
} // namespace Ui

QT_END_NAMESPACE

#endif // SETTINGS_WINDOWYXDVYY_H
