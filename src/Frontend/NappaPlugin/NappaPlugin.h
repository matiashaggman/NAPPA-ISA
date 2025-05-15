// Plugin.h  ────────────────────────────────────────────────────────────────
#pragma once
#include <QObject>
#include <QCheckBox>
#include <QVBoxLayout>
#include <QApplication>
#include <QJsonObject>

#include "../Common/inAppPlugin.h" 
#include "../Frontend/NappaMainWindow.h"
#include "../Frontend/SettingsWindow.h"

class Plugin : public QObject,
    public INappaPlugin
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID INappaPlugin_iid FILE "plugin.json")
	Q_INTERFACES(INappaPlugin)

public:
    float version() const override { return 1.0f; }
    void  boot(NappaMainWindow*) override {}

    void buildSettingsPage(SettingsWindow* dlg,
        const QJsonObject& current) override
    {
        //auto* box = dlg->ui.classifierInputGroupBox;
        //if (!box->layout())
        //    box->setLayout(new QVBoxLayout(box));

        //auto* cb = new QCheckBox("Enable experimental mode", box);
        //cb->setObjectName("expCheck");
        //cb->setChecked(current.value("experimental").toBool(false));
        //box->layout()->addWidget(cb);
    }

    void collectSettings(SettingsWindow* dlg,
        QJsonObject& inOutRootSettings) const override
    {
        //auto* cb = dlg->findChild<QCheckBox*>("expCheck");
        //inOutRootSettings["experimental"] = cb && cb->isChecked();
    }
};
