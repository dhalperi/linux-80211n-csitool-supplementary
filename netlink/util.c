#include "util.h"

#include <arpa/inet.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <sys/socket.h>
#include <linux/if_ether.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

#include "iwl_structs.h"

double db(double x)
{
	if (fabs(x) < 0.0001) return -10000;
	return log(x) * _10_BY_LN_10;
}
double exp_10(double x)
{
	return exp(x * LN_10_BY_10);
}
