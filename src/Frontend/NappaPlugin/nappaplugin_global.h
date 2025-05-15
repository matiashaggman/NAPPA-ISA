#pragma once

#include <QtCore/qglobal.h>

#ifndef BUILD_STATIC
# if defined(NAPPAPLUGIN_LIB)
#  define NAPPAPLUGIN_EXPORT Q_DECL_EXPORT
# else
#  define NAPPAPLUGIN_EXPORT Q_DECL_IMPORT
# endif
#else
# define NAPPAPLUGIN_EXPORT
#endif
