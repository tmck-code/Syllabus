build:
	docker-compose build syllabus

syllabus: build
	docker-compose up
	docker-compose down

.PHONY: build syllabus
