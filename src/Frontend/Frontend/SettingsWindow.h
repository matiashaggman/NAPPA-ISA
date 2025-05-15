#pragma once
#include "UiSettingsWindow.h"

#include <QDialog>
#include <QJsonObject>
#include <QJsonDocument>

class SettingsWindow : public QDialog
{
    Q_OBJECT
public:
    explicit SettingsWindow(QWidget* parent = nullptr,
        const QJsonObject current_settings = QJsonObject());
    ~SettingsWindow();

    void updateLayout();
    QJsonObject refreshSettings();

    void mergeSettings(const QJsonObject& patch);

    Ui::Settings ui;
    QJsonObject settings;
    void initUI();
};


