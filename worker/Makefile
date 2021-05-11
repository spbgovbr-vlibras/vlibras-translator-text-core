CURR_DIR	:=	$(shell pwd)
UTILS_PYCACHE	:=	"$(CURR_DIR)/core/utils/__pycache__"

CORE_CONFIG_FILE	:=	"$(CURR_DIR)/config/settings.ini"
LOGGER_CONFIG_FILE	:=	"$(CURR_DIR)/config/logging.ini"

install:
	@bash install.sh

start:
	@CORE_CONFIG_FILE=$(CORE_CONFIG_FILE) \
	LOGGER_CONFIG_FILE=$(LOGGER_CONFIG_FILE) \
	python core/worker.py

dev:
	@:$(eval CORE_CONFIG_FILE := "$(CURR_DIR)/config/settings-dev.ini")
	@:$(eval LOGGER_CONFIG_FILE := "$(CURR_DIR)/config/logging-dev.ini")

clean:
	@echo -n "Cleaning... "
	@$(RM) -r $(UTILS_PYCACHE)
	@echo "\33[32;5mOK\033[m" || echo "\33[31;5mERROR\33[m"

.PHONY: install start dev clean
