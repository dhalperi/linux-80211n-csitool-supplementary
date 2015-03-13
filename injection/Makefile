CFLAGS = -O3 -Wall -static -Wno-unknown-pragmas
CC = gcc

ALL = random_packets

all: $(ALL)

clean:
	rm $(ALL)

random_packets: random_packets.c util.o
	$(CC) $(CFLAGS) -o $@ $^ -lorcon -lm -lrt

util.o: util.c util.h Makefile
