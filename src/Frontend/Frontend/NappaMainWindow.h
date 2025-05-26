#pragma once

#include "../Common/inAppPlugin.h"

#include "UiMainWindow.h"
#include "UiSettingsWindow.h"

#include "ThreadWorker.h"
#include "TimeDateGridWindow.h"
#include "SettingsWindow.h"


#include <QMainWindow>
#include <QVector>
#include <QPluginLoader>

class NappaMainWindow : public QDialog
{
    Q_OBJECT
public:
    explicit NappaMainWindow(QWidget* parent = nullptr);
    ~NappaMainWindow();

private slots:
	void onAdvancedSettingsButtonClicked();
    void onBrowseInputButtonClicked();
    void onBrowseOutputButtonClicked();
    void onSelectPeriodsButtonClicked();
    void onAnalyzeButtonClicked();

    void onUpdateStatus(const float statusCode, const QString& msg = QString());
    void onImportFinished(const QJsonObject& response);


    void connectToServer(const QString& ownIp);

protected:
    void dragEnterEvent(QDragEnterEvent* event) override;
    void dropEvent(QDropEvent* event) override;

private:
    void initUI();
	void loadPlugin(const QString& path);
    void loadSettings(const QString&);
    void refreshSettings();
    void saveSettings(const QString&);
    void importRecording();
    void fetchPublicIP();

    Ui::NappaDialog ui;
    SettingsWindow* settingsWindow;
    TimeDateGridWindow* timeGridWindow;

    QJsonObject settings;
    QJsonObject userData;
    QString publicIP;
    
    QPluginLoader* pluginLoader_{ nullptr };
    INappaPlugin* plugin{ nullptr };

	const QString settingsPath = "settings.json";
	const QString version = "1.4";
};
