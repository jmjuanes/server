.PHONY: build install publish

# Install all dependencies
install:
	@# Install node dependencies
	npm install
	@# Install python dependencies
	pip install -t lib -r requirements.txt

# Build the service
build: 
	@## Clean deploy folder
	@#rm -rf deploy && mkdir deploy
	@## Copy configuration file to deploy folder
	@#cp configs/${service}.json deploy/config.json
	@## Copy scripts files
	@#cp src/*py deploy/
	@#cp appengine_config.py deploy/
	@#cp .gitignore deploy/
	@#cp -R lib deploy/
	@#cp app.yaml deploy/
	@## Build static files from configuration file
	rm -rf static && mkdir static
	node ./scripts/build.js

# Publish the service
deploy:
	@## Get the current project to deploy
	$(eval SERVER_PROJECT := $(shell node scripts/get-project.js))
	@echo "Deploying service to project: ${SERVER_PROJECT}"
	@## Deploy service to google cloud
	gcloud app deploy app.yaml --project ${SERVER_PROJECT}

