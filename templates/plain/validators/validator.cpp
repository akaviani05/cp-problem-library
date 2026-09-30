#include "testlib.h"

#error CPPL_TEMPLATE_UNFINISHED
int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    // Use named reads with bounds, explicit readSpace/readEoln, then readEof.
    // Check semantic constraints (connectivity, uniqueness, etc.) explicitly.
    inf.readEof();
}
