#include <QApplication>
#include "NappaMainWindow.h"

int main(int argc, char* argv[])
{
    QApplication app(argc, argv);

    NappaMainWindow mainDialog;
    mainDialog.exec();

    return 0;
}