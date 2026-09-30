"""Exact arithmetic oracle, independent of C++ integer width and string arithmetic."""
import sys

a, b = map(int, sys.stdin.buffer.read().split())
print(a - b)
