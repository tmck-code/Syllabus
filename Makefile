build:
	docker-compose build syllabus

syllabus:
	docker-compose up
	docker-compose down

.PHONY: build syllabus
