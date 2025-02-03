#!/bin/bash
set -e

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
	docker build --no-cache -t dainok/${IMAGE}:${NEXT_VERSION} -t dainok/${IMAGE}:latest .
	cd ..
done

# Push do Docker Hub
for IMAGE in ${IMAGES}; do
	docker push dainok/${IMAGE}:${NEXT_VERSION}
	docker push dainok/${IMAGE}:latest
done
