all: parse_log log_to_file 

KERNEL = $(strip $(shell uname -r))
KERNEL_INCLUDE = -I /usr/src/linux-headers-$(KERNEL)/include

log_to_file: log_to_file.c Makefile
	gcc $(KERNEL_INCLUDE) log_to_file.c -o log_to_file

parse_log: parse_log.c Makefile
	gcc parse_log.c -o parse_log

clean:
	rm -f log_to_file
