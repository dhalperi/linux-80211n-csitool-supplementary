all: print_packets get_first_bfee parse_log log_to_file

KERNEL = $(strip $(shell uname -r))
KERNEL_INCLUDE = -I /usr/src/linux-headers-$(KERNEL)/include
CFLAGS = -Wall -Werror

log_to_file: log_to_file.c Makefile
	gcc $(KERNEL_INCLUDE) log_to_file.c -o log_to_file

clean:
	rm -f get_first_bfee log_to_file print_packets parse_log
