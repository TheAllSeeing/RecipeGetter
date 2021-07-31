#!/usr/bin/env sh

err_file=$(mktemp)
python3 -c "from scrape_data import reset; reset()" 2>"$err_file"  \
&& python3 ./assemble_data.py 2>"$err_file" \
&& python3 ./classifier.py 2>"$err_file" \

# Suppress warning to use command in if block directly rather than checking status later. I think it's more mess
# than it's worth.
# shellcheck disable=SC2181
if [ "$?" -ne 0 ]; then
  echo "An error occurred. Check $err_file for details."
  cat "$err_file"
fi
