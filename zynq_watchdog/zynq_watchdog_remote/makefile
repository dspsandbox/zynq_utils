# -------- Configuration --------
PY_SRC      := zynq_watchdog.py
PY_DST      := /usr/share/zynq_watchdog.py

SERVICE_SRC := zynq_watchdog.service
SERVICE_DST := /etc/systemd/system/zynq_watchdog.service

SERVICE_NAME := zynq_watchdog

# -------- Targets --------

.PHONY: install uninstall install-py install-service enable restart reload all clean stop disable

all: install

install: install-py install-service reload enable restart
uninstall: stop disable 


install-py:
	@echo "Installing Python script..."
	cp $(PY_SRC) $(PY_DST)

install-service:
	@echo "Installing systemd service..."
	cp $(SERVICE_SRC) $(SERVICE_DST)

reload:
	@echo "Reloading systemd daemon..."
	systemctl daemon-reexec
	systemctl daemon-reload

enable:
	@echo "Enabling service $(SERVICE_NAME)..."
	systemctl enable $(SERVICE_NAME)

restart:
	@echo "Restarting service $(SERVICE_NAME)..."
	systemctl restart $(SERVICE_NAME)

disable:
	@echo "Disabling service $(SERVICE_NAME)..."
	systemctl disable $(SERVICE_NAME)

stop:
	@echo "Stopping service $(SERVICE_NAME)..."
	systemctl stop $(SERVICE_NAME)


clean: uninstall 
	@echo "Removing installed files..."
	rm -f $(PY_DST)
	rm -f $(SERVICE_DST)
