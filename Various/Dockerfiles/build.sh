#!/bin/bash


if [ "$1" == "" ]; then
	# Compile all images
	IMAGES=$(ls -1d */ | cut -d"/" -f1)
else
	# Compile single image
	IMAGES=$1
fi

for IMAGE in ${IMAGES}; do
	# Read current version
	VERSION=$(cat ${IMAGE}/Dockerfile | grep VERSION | cut -d"=" -f2)

	# Update VERSION on Dockerfile
	NEXT_VERSION=$((${VERSION} + 1))
	sed -i "s/ARG VERSION.*/ARG VERSION=${NEXT_VERSION}/g" ${IMAGE}/Dockerfile

	# Build and tag image
	cd ${IMAGE}
	echo ${IMAGE}
	docker build -t dainok/ews:${NEXT_VERSION} -t dainok/ews:latest .
	cd ..
done

