all: log_to_file

KERNEL = $(strip $(shell uname -r))
INCLUDE = -I /usr/src/linux-headers-$(KERNEL)/include

log_to_file: log_to_file.c Makefile
	gcc $(INCLUDE) log_to_file.c -o log_to_file

clean:
	rm -f log_to_file
