DC = docker-compose
DC_FILE = docker-compose.yaml

.PHONY: all
all:
	${DC} -f ${DC_FILE} up -d

.PHONY: drop-all
drop-all:
	${DC} -f ${DC_FILE} down

.PHONY: logs
logs:
	${DC} -f ${DC_FILE} logs -f
