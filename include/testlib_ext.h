#ifndef CP_PROBLEM_LIBRARY_TESTLIB_EXT_H
#define CP_PROBLEM_LIBRARY_TESTLIB_EXT_H

// Project helpers belong here; the vendored testlib.h is never modified.
#include "testlib.h"

namespace cp {
inline void require_output_eof() {
    if (!ouf.seekEof())
        quitf(_pe, "unexpected tokens after the answer");
}
}  // namespace cp

#endif
