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
	gcloud app deploy app.yaml --project ${project}

