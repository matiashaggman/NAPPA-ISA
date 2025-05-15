#pragma once
#include <QtPlugin>

class NappaMainWindow;
class SettingsWindow;
class QJsonObject;

class INappaPlugin
{
public:
    virtual float version() const = 0;
    virtual ~INappaPlugin() = default;
    virtual void boot(NappaMainWindow* host) = 0;

    virtual void buildSettingsPage(SettingsWindow* dlg,
        const QJsonObject& current) = 0;

    virtual void collectSettings(SettingsWindow* dlg,
        QJsonObject& inOutRootSettings) const = 0;
};
#define INappaPlugin_iid "com.nappa.uiplugin/1.0"
Q_DECLARE_INTERFACE(INappaPlugin, INappaPlugin_iid)