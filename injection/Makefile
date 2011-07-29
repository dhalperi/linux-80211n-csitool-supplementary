KERNEL = $(strip $(shell uname -r))
INCLUDE = -I /usr/src/linux-headers-$(KERNEL)/include
CC_OPTS = -O3 -Wall -static -Wno-unknown-pragmas
CC = gcc

CFLAGS = $(CC_OPTS) $(INCLUDE)

ALL = random_packets

all: $(ALL)

clean:
	rm $(ALL)

random_packets: random_packets.c util.o
	$(CC) $(CFLAGS) -o $@ $^ -lorcon -lm -lrt

util.o: util.c util.h Makefile
