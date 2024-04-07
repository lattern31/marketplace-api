DC = docker-compose
DC_FILE = docker-compose.yaml
DC_CI_FILE = docker-compose-ci.yaml

.PHONY: all
all:
	${DC} -f ${DC_FILE} up -d

.PHONY: drop
drop-all:
	${DC} -f ${DC_FILE} down

.PHONY: ci
ci:
	${DC} -f ${DC_CI_FILE} up -d

.PHONY: ci
drop-ci:
	${DC} -f ${DC_CI_FILE} down

.PHONY: logs
logs:
	${DC} -f ${DC_FILE} logs -f
