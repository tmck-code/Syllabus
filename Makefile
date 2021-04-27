build:
	docker-compose build lab

lab: build
	docker-compose up
	docker-compose down

.PHONY: build lab
