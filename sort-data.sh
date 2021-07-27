#!/bin/sh

# This script receives a recipe URL and prints a list of all textual paragraphs it contains, allowing me
# to filter output contents to ignore instructions and ingredients.
# This moderately helps gathering data that is neither instructions nor ingredients, to avoid false positives on links
# and comments.

get_data() {
  python3 -c "from main import get_paragraphs, get_html; print('\n'.join(get_paragraphs(get_html('$1'))))"
}

get_data "$1" > /tmp/neither

echo waiting for you to finish editing...
emacs /tmp/neither # Let user filter manually
cat /tmp/neither >> neither.txt


