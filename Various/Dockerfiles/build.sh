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
	VERSION_AD=$(cat ${IMAGE}/Dockerfile | grep VERSION_AD | cut -d"=" -f2)

	# Update VERSION_AD on Dockerfile
	NEXT_VERSION_AD=$((${VERSION_AD} + 1))
	sed -i "s/ARG VERSION_AD.*/ARG VERSION_AD=${NEXT_VERSION_AD}/g" ${IMAGE}/Dockerfile

	# Build and tag image
	cd ${IMAGE}
	echo ${IMAGE}
	docker build --no-cache -t dainok/${IMAGE}:${NEXT_VERSION_AD} -t dainok/${IMAGE}:latest .
	cd ..
done

# Push do Docker Hub
for IMAGE in ${IMAGES}; do
	docker push dainok/${IMAGE}:${NEXT_VERSION_AD}
	docker push dainok/${IMAGE}:latest
done
