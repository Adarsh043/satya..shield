import json
import re

with open('src/i18n.ts', 'r') as f:
    content = f.read()

# I will just use sed or multi_replace directly.
