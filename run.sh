#!/bin/env sh
err_file=$(mktemp)
python3 -c "from main import get_recipe_json; print(get_recipe_json('$1'))" 2>"$err_file"

# Suppress warning to use command in if block directly rather than checking status later. I think it's more mess
# than it's worth.
# shellcheck disable=SC2181
if [ "$?" -ne 0 ]; then
  echo "An error occurred. Check $err_file for details."
fi

