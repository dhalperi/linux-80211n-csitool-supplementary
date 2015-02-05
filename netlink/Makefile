all: print_packets get_first_bfee parse_log log_to_file nl_bf_to_eff

KERNEL = $(strip $(shell uname -r))
KERNEL_INCLUDE = -I /lib/modules/$(KERNEL)/build/include
CFLAGS = -Wall -Werror $(KERNEL_INCLUDE)
LDLIBS = -lm
CC = gcc

nl_bf_to_eff: nl_bf_to_eff.c bf_to_eff.o iwl_nl.o util.o q_approx.o

clean:
	rm -f *.o get_first_bfee log_to_file print_packets parse_log nl_bf_to_eff
