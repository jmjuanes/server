.PHONY: build install publish

# Install all dependencies
install:
	@# Install node dependencies
	npm install
	@# Install python dependencies
	pip install -t lib -r requirements.txt

# Build the service
build: 
	node ./scripts/build.js

# Publish the service
deploy:
	gcloud app deploy beta.yaml --project siimple-documentation

