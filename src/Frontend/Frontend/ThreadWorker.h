#pragma once  
#include <QThread>  
#include <QJsonObject>  
#include <QJsonDocument>  
#include <QUrl>

#define STATUS_USER_CONNECTED 1
#define STATUS_USER_CONNECT_ERROR -1

#define STATUS_IMPORT_SUCCESS 3
#define STATUS_IMPORT_ERROR -3

#define STATUS_ANALYZE_SUCCESS 4
#define STATUS_ANALYZE_ERROR -4

class ThreadWorker : public QThread {  
   Q_OBJECT  
public:  
   enum CallType {Start, Import, Analysis};  

   explicit ThreadWorker(QObject* parent = nullptr,   
       const QString inputFile = QString(),
       const QString outputFile = QString(),
       const QString settingsPath = QString(),
       const QJsonObject userData = QJsonObject(),
       CallType type = Start)
   {  
       this->inputFile = inputFile;  
       this->outputFile = outputFile;  
       this->settingsPath = settingsPath;  
       this->callType = type;  
       this->userData = userData;  
   }  

   void run() override;

signals:  
   void onUpdateStatus(const float statusCode, const QString& msg = QString());
   void onUpdateRequestFinished(const QJsonObject&);
   void onImportFinished(const QJsonObject&);
   void onAnalyzeFinished();

private:  
   void startServerAndUpdateRequest();
   void uploadAndImportRequest();
   void uploadAndAnalyzeRequest();

   QString inputFile;  // path to .zip archive  
   QString outputFile; // path to .zip archive  
   CallType callType;  
   QString settingsPath; // path to settings.json  
   QJsonObject userData;

   const QString serverUrl = "https://8000-01jshk18q2p91hqcm4arhwcffb.cloudspaces.litng.ai";  
   const QUrl startupUrl = QUrl(serverUrl + "/startup");
   const QUrl importUrl = QUrl(serverUrl + "/import");
   const QUrl analysisUrl = QUrl(serverUrl + "/analysis");
};
