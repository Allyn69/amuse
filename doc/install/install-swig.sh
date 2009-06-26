#!/bin/sh
#
# script to install amuse build system from scratch
#
# author: Arjen van Elteren
# date  : 2009 - 05 -18
#


APPVER=1.3.39
APPFILE=swig-${APPVER}.tar.gz
APP_DIR=swig-${APPVER}
URL=http://kent.dl.sourceforge.net/sourceforge/swig/${APPFILE}

DOWNLOAD_DIR=_downloaded
BUILD_DIR=_build
SOURCE_DIR=_source

#rm -Rf ${DOWNLOAD_DIR}
#rm -Rf ${SOURCE_DIR}
#rm -Rf ${BUILD_DIR}
mkdir ${DOWNLOAD_DIR}
mkdir ${SOURCE_DIR}
mkdir ${BUILD_DIR}

echo "Downloading archive file..."
cd  ${DOWNLOAD_DIR}
if [ -e ${APPFILE} ]; then
	echo "...File already downloaded";
else
	curl -O ${URL} ;
fi
echo "...Done"

cd ..
cd ${SOURCE_DIR}

echo "Unpacking source files.."
rm -Rf ${APPFILE}
tar -xf ../${DOWNLOAD_DIR}/$APPFILE
echo "..Done"

cd ..

echo "Building files.."
cd ${BUILD_DIR}
mkdir ${APP_DIR}
cd ${APP_DIR}

#--with-pydebug
../../${SOURCE_DIR}/${APP_DIR}/configure \
	--prefix=${PREFIX} \
	--with-dyld 
make 
make install
echo "..Done"
