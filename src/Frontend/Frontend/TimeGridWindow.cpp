#include "TimeDateGridWindow.h"
#include <QCloseEvent>

TimeDateGridWindow::TimeDateGridWindow(QWidget* parent)
    : QDialog(parent), rows(0)
{
    setWindowTitle("Select sleep periods for report pages");

    QVBoxLayout* mainLayout = new QVBoxLayout(this);
    gridLayout = new QGridLayout();
    mainLayout->addLayout(gridLayout);

	QPushButton* saveButton = new QPushButton("Save and close", this);
	connect(saveButton, &QPushButton::clicked, this, &TimeDateGridWindow::onSaveButtonClicked);

    QPushButton* addButton = new QPushButton("Add new sleep period", this);
    connect(addButton, &QPushButton::clicked, this, &TimeDateGridWindow::onAddPeriodClicked);

    QHBoxLayout* buttonLayout = new QHBoxLayout();
    buttonLayout->addStretch();
    buttonLayout->addWidget(addButton);
	buttonLayout->addWidget(saveButton);

    mainLayout->addStretch();
    mainLayout->addLayout(buttonLayout);

    setLayout(mainLayout);
}

void TimeDateGridWindow::onSaveButtonClicked()
{
	refreshPeriods();
    accept();
}
void TimeDateGridWindow::onAddPeriodClicked()
{
    addPeriod("", "");
}


void TimeDateGridWindow::addPeriod(const QString& startString, const QString& endString)
{
    QLabel* labelStart = new QLabel("Start:", this);
    QLabel* labelEnd = new QLabel("End:", this);
    QDateTimeEdit* startEdit = new QDateTimeEdit(this);
    QDateTimeEdit* endEdit = new QDateTimeEdit(this);
    QCheckBox* includeCheckBox = new QCheckBox("Include", this);
    includeCheckBox->setChecked(true);

    if (!startString.isEmpty())
        startEdit->setDateTime(QDateTime::fromString(startString, "yyyy-MM-dd HH:mm:ss"));
    if (!endString.isEmpty())
        endEdit->setDateTime(QDateTime::fromString(endString, "yyyy-MM-dd HH:mm:ss"));

    gridLayout->addWidget(labelStart, rows, 0);
    gridLayout->addWidget(startEdit, rows, 1);
    gridLayout->addWidget(labelEnd, rows, 2);
    gridLayout->addWidget(endEdit, rows, 3);
    gridLayout->addWidget(includeCheckBox, rows, 4);

    dateEdits.append({ startEdit, endEdit, includeCheckBox });
    rows++;
}

void TimeDateGridWindow::refreshPeriods()
{
    periods.clear();
    for (const auto& row : dateEdits) {
        if (row.include->isChecked()) {
            QString start = row.startEdit->dateTime().toString("yyyy-MM-dd HH:mm:ss");
            QString end = row.endEdit->dateTime().toString("yyyy-MM-dd HH:mm:ss");
            periods.append(qMakePair(start, end));
        }
    }
#ifdef QT_DEBUG
    qDebug() << "Periods refreshed. Current periods:";
    for (const auto& period : periods) {
        qDebug() << "Start:" << period.first << ", End:" << period.second;
    }
#endif
    // Sort the periods by start time.
    std::sort(periods.begin(), periods.end(), [](const QPair<QString, QString>& a, const QPair<QString, QString>& b) {
        return QDateTime::fromString(a.first, "yyyy-MM-dd HH:mm:ss") < QDateTime::fromString(b.first, "yyyy-MM-dd HH:mm:ss");
        });
#ifdef QT_DEBUG
    qDebug() << "Periods sorted. Current periods:";
    for (const auto& period : periods) {
        qDebug() << "Start:" << period.first << ", End:" << period.second;
    }
#endif
}


void TimeDateGridWindow::closeEvent(QCloseEvent* event)
{
    this->periods.clear();
    refreshPeriods();
    accept();
    QDialog::closeEvent(event);
}
void TimeDateGridWindow::loadPeriods(const QList<QPair<QString, QString>>& input)
{
    for (const auto& pair : input) {
        addPeriod(pair.first, pair.second);
    }
}


// Old versions: use delete buttons to remove rows at once (buggy/unstable). Deprecated/removed as of version 1.52 and replaced with
// checkboxes "include" on each row instead.

/*
void TimeDateGridWindow::addPeriod(const QString& startString, const QString& endString)
{
    QLabel* labelStart = new QLabel("Start:", this);
    QLabel* labelEnd = new QLabel("End:", this);
    QDateTimeEdit* startEdit = new QDateTimeEdit(this);
    QDateTimeEdit* endEdit = new QDateTimeEdit(this);

    if (!startString.isEmpty())
        startEdit->setDateTime(QDateTime::fromString(startString, "yyyy-MM-dd HH:mm:ss"));
    if (!endString.isEmpty())
        endEdit->setDateTime(QDateTime::fromString(endString, "yyyy-MM-dd HH:mm:ss"));

    QPushButton* deleteButton = new QPushButton("Delete", this);
    connect(deleteButton, &QPushButton::clicked, this, &TimeDateGridWindow::onDeletePeriodClicked);

    gridLayout->addWidget(labelStart, rows, 0);
    gridLayout->addWidget(startEdit, rows, 1);
    gridLayout->addWidget(labelEnd, rows, 2);
    gridLayout->addWidget(endEdit, rows, 3);
    gridLayout->addWidget(deleteButton, rows, 4);

    dateEdits.append(qMakePair(startEdit, endEdit));
    rows++;
}

void TimeDateGridWindow::onDeletePeriodClicked()
{
    QPushButton* senderBtn = qobject_cast<QPushButton*>(sender());
    if (!senderBtn) return;

    int index = gridLayout->indexOf(senderBtn);
    int row, col, rowSpan, colSpan;
    gridLayout->getItemPosition(index, &row, &col, &rowSpan, &colSpan);

    for (int c = 0; c < gridLayout->columnCount(); ++c) {
        QLayoutItem* item = gridLayout->itemAtPosition(row, c);
        if (item && item->widget()) {
            item->widget()->deleteLater();
        }
    }

    if (row < dateEdits.size()) {
        dateEdits.removeAt(row);
    }

    rows--;
}

void TimeDateGridWindow::refreshPeriods()
{
	for (const auto& pair : dateEdits) {
		QString start = pair.first->dateTime().toString("yyyy-MM-dd HH:mm:ss");
		QString end = pair.second->dateTime().toString("yyyy-MM-dd HH:mm:ss");
		periods.append(qMakePair(start, end));
	}
#ifdef QT_DEBUG
	qDebug() << "Periods refreshed. Current periods:";
	for (const auto& period : periods) {
		qDebug() << "Start:" << period.first << ", End:" << period.second;
	}
#endif
	// Some logic elsewhere might fail if sleep periods list is not ordered. Sort the periods by start time:
	std::sort(periods.begin(), periods.end(), [](const QPair<QString, QString>& a, const QPair<QString, QString>& b) {
		return QDateTime::fromString(a.first, "yyyy-MM-dd HH:mm:ss") < QDateTime::fromString(b.first, "yyyy-MM-dd HH:mm:ss");
	});
#ifdef QT_DEBUG
	qDebug() << "Periods sorted. Current periods:";
	for (const auto& period : periods) {
		qDebug() << "Start:" << period.first << ", End:" << period.second;
	}
#endif
}*/