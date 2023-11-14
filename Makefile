CURR_DIR	:=	$(shell pwd)
UTIL_PYCACHE	:=	"$(CURR_DIR)/src/util/__pycache__"

CORE_CONFIG_FILE	:=	"$(CURR_DIR)/src/config/settings.ini"
LOGGER_CONFIG_FILE	:=	"$(CURR_DIR)/src/config/logging.ini"

install:
	@bash install.sh

start:
	@CORE_CONFIG_FILE=$(CORE_CONFIG_FILE) \
	LOGGER_CONFIG_FILE=$(LOGGER_CONFIG_FILE) \
	python src/worker.py

dev:
	@:$(eval CORE_CONFIG_FILE := "$(CURR_DIR)/src/config/settings-dev.ini")
	@:$(eval LOGGER_CONFIG_FILE := "$(CURR_DIR)/src/config/logging-dev.ini")

stage:
	@:$(eval LOGGER_CONFIG_FILE := "$(CURR_DIR)/src/config/logging-dev.ini")

clean:
	@echo -n "Cleaning... "
	@$(RM) -r $(UTIL_PYCACHE)
	@echo "\33[32;5mOK\033[m" || echo "\33[31;5mERROR\33[m"

.PHONY: install start dev stage clean
