#pragma once
#include <QDialog>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QDateTimeEdit>
#include <QLabel>
#include <QPushButton>
#include <QDateTime>
#include <QList>
#include <QPair>
#include <QString>

class TimeDateGridWindow : public QDialog {
    Q_OBJECT

public:
    explicit TimeDateGridWindow(QWidget* parent = nullptr);

    void loadPeriods(const QList<QPair<QString, QString>>& input);

    QList<QPair<QString, QString>> periods;

protected:
    void closeEvent(QCloseEvent* event) override;
    

private slots:
	void onSaveButtonClicked();
    void onAddPeriodClicked();
    void onDeletePeriodClicked();

private:
    void addPeriod(const QString& startString, const QString& endString);
   
    QGridLayout* gridLayout;
    QList<QPair<QDateTimeEdit*, QDateTimeEdit*>> dateEdits;
    int rows;
};
