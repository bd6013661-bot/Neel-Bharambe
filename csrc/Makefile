CC      ?= gcc
CFLAGS  ?= -O3 -Wall -Wextra -std=c11 -march=native
BINDIR  ?= ../bin

all: $(BINDIR)/ocgen $(BINDIR)/occheck

$(BINDIR)/ocgen: ocgen.c | $(BINDIR)
	$(CC) $(CFLAGS) -o $@ $<

# The checker is the trusted base: built without -march=native and without
# aggressive optimisation, so the binary a referee reproduces matches the source
# as closely as possible.
$(BINDIR)/occheck: occheck.c | $(BINDIR)
	$(CC) -O2 -Wall -Wextra -std=c11 -o $@ $<

$(BINDIR):
	mkdir -p $(BINDIR)

clean:
	rm -f $(BINDIR)/ocgen $(BINDIR)/occheck

.PHONY: all clean
