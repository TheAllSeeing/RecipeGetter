#!/bin/env sh
python3 -c "from main import get_recipe_json; print(get_recipe_json('$1'))" 2>/dev/null
