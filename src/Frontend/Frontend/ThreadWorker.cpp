#include "ThreadWorker.h"
#include <QJsonParseError>  
#include <QFile>  
#include <QDir>  
#include <QNetworkAccessManager>  
#include <QNetworkRequest>  
#include <QHttpMultiPart>  
#include <QNetworkReply>  
#include <QFileInfo>  
#include <QTimer>  
#include <QObject>
#include <QEventLoop>
#include <QMessageBox>

void ThreadWorker::run()
{
    if (this->callType == Analysis)
    {
        this->uploadAndAnalyzeRequest();
    }
    else if (this->callType == Import) {
        this->uploadAndImportRequest();
    }
    else if (this->callType == Start) {
        this->startServerAndUpdateRequest();

    }
}

void ThreadWorker::startServerAndUpdateRequest()
{   
    QNetworkRequest request(this->startupUrl);

	QJsonDocument payload(this->userData);
    QByteArray data = payload.toJson();

    QNetworkAccessManager manager;
    QNetworkReply* reply = manager.post(request, data);
    reply->setParent(this);

    QEventLoop loop;
    connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();

    if (reply->error() == QNetworkReply::NoError) {
        QByteArray response = reply->readAll();
        QJsonParseError parseError;
        QJsonDocument responseDoc = QJsonDocument::fromJson(response, &parseError);

        if (parseError.error == QJsonParseError::NoError && responseDoc.isObject()) {
            QJsonObject responseObj = responseDoc.object();
            emit onUpdateStatus(STATUS_USER_CONNECTED);
			emit onUpdateRequestFinished(responseObj);
        }
    }
    else {
		emit onUpdateStatus(STATUS_USER_CONNECT_ERROR, reply->errorString());
    }

    reply->deleteLater();
}


void ThreadWorker::uploadAndImportRequest() {
    QNetworkRequest request(this->importUrl);

    QHttpMultiPart* multiPart = new QHttpMultiPart(QHttpMultiPart::FormDataType);

    QFile* zipFile = new QFile(this->inputFile);
    if (!zipFile->open(QIODevice::ReadOnly)) {
        emit onUpdateStatus(STATUS_IMPORT_ERROR, "Failed to open input file.");
        return;
    }

    QHttpPart zipPart;
    zipPart.setHeader(QNetworkRequest::ContentDispositionHeader,
        QVariant("form-data; name=\"zip_archive\"; filename=\"" + QFileInfo(*zipFile).fileName() + "\""));
    zipPart.setBodyDevice(zipFile);
    zipFile->setParent(multiPart);
    multiPart->append(zipPart);

    QFile* settingsFile = new QFile(this->settingsPath);
    if (!settingsFile->open(QIODevice::ReadOnly)) {
        emit onUpdateStatus(STATUS_IMPORT_ERROR, "Failed to read settings file.");
        return;
    }

    QHttpPart jsonPart;
    jsonPart.setHeader(QNetworkRequest::ContentDispositionHeader,
        QVariant("form-data; name=\"settings\"; filename=\"" + QFileInfo(*settingsFile).fileName() + "\""));
    jsonPart.setBodyDevice(settingsFile);
    settingsFile->setParent(multiPart);
    multiPart->append(jsonPart);

    QNetworkAccessManager* manager = new QNetworkAccessManager();
    QNetworkReply* reply = manager->post(request, multiPart);
    multiPart->setParent(reply);

    QEventLoop loop;
    connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();

    if (reply->error() == QNetworkReply::NoError) {
        QByteArray response = reply->readAll();
        QJsonParseError parseError;
        QJsonDocument doc = QJsonDocument::fromJson(response, &parseError);

        if (parseError.error == QJsonParseError::NoError && doc.isObject()) {
            QJsonObject responseObj = doc.object();
            emit onUpdateStatus(STATUS_IMPORT_SUCCESS);
            emit onImportFinished(responseObj);
        }
        else {
            emit onUpdateStatus(STATUS_IMPORT_ERROR, "Failed to process server response.");
        }
    }
    else {
        QByteArray response = reply->readAll();
        QJsonParseError parseError;
        QJsonDocument errorDoc = QJsonDocument::fromJson(response, &parseError);

        if (parseError.error == QJsonParseError::NoError && errorDoc.isObject()) {
            QJsonObject errorObj = errorDoc.object();
            QString errorMsg = errorObj["error"].toString();
            QString traceback = errorObj["traceback"].toString();
            emit onUpdateStatus(STATUS_IMPORT_ERROR, errorMsg + "\n\nFull error traceback:\n" + traceback);
        }
        else {
            emit onUpdateStatus(STATUS_IMPORT_ERROR, reply->errorString());
        }
    }
    manager->deleteLater();
    reply->deleteLater();
    zipFile->close();
    settingsFile->close();
}

void ThreadWorker::uploadAndAnalyzeRequest() {

    QNetworkRequest request(this->analysisUrl);

    QHttpMultiPart* multiPart = new QHttpMultiPart(QHttpMultiPart::FormDataType);
    QFile* zipFile = new QFile(this->inputFile);
    if (!zipFile->open(QIODevice::ReadOnly)) {
        emit onUpdateStatus(STATUS_ANALYZE_ERROR, "Failed to open input file.");
        return;
    }

    QHttpPart zipPart;
    zipPart.setHeader(QNetworkRequest::ContentDispositionHeader,
        QVariant("form-data; name=\"zip_archive\"; filename=\"" + QFileInfo(*zipFile).fileName() + "\""));
    zipPart.setBodyDevice(zipFile);
    zipFile->setParent(multiPart);
    multiPart->append(zipPart);

    QFile* settingsFile = new QFile(this->settingsPath);
    if (!settingsFile->open(QIODevice::ReadOnly)) {
        emit onUpdateStatus(STATUS_ANALYZE_ERROR, "Failed to read settings file.");
        return;
    }

    QHttpPart jsonPart;
    jsonPart.setHeader(QNetworkRequest::ContentDispositionHeader,
        QVariant("form-data; name=\"settings\"; filename=\"" + QFileInfo(*settingsFile).fileName() + "\""));
    jsonPart.setBodyDevice(settingsFile);
    settingsFile->setParent(multiPart);
    multiPart->append(jsonPart);

    QNetworkAccessManager* manager = new QNetworkAccessManager();
    QNetworkReply* reply = manager->post(request, multiPart);
    multiPart->setParent(reply);

    QEventLoop loop;
    connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();

    if (reply->error() == QNetworkReply::NoError) {
        QFile output(outputFile);
        if (output.open(QIODevice::WriteOnly)) {
            output.write(reply->readAll());
            output.close();
            emit onUpdateStatus(STATUS_ANALYZE_SUCCESS);
            emit onAnalyzeFinished();
        }
        else {
            emit onUpdateStatus(STATUS_ANALYZE_ERROR, "Failed to write output file.");
        }
    }
    else {
        QByteArray response = reply->readAll();
        QJsonParseError parseError;
        QJsonDocument errorDoc = QJsonDocument::fromJson(response, &parseError);

        if (parseError.error == QJsonParseError::NoError && errorDoc.isObject()) {
            QJsonObject errorObj = errorDoc.object();
            QString errorMsg = errorObj["error"].toString();
            QString traceback = errorObj["traceback"].toString();
            emit onUpdateStatus(STATUS_ANALYZE_ERROR, errorMsg + "\n\nFull error traceback:\n" + traceback);
        }
        else {
            emit onUpdateStatus(STATUS_ANALYZE_ERROR, reply->errorString());
        }
	}
	reply->deleteLater();
	zipFile->close();
	settingsFile->close();
}
