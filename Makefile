build:
	docker-compose build syllabus

syllabus:
	docker-compose up
	docker-compose down

syllabus-intermediate:
	docker-compose up syllabus-intermediate
	docker-compose down

.PHONY: build syllabus syllabus-intermediate
