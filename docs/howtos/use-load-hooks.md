# Use Process Hooks

There are three settings, FEEDS_FILTER_TITLE, FEEDS_FILTER_AUTHORS and
FEEDS_FILTER_TAGS, which you can use to specify the paths to functions 
that the feed loader will call to process the title, list of authors and 
list of tags loaded for each entry in a feed. This How-To has an example 
for each setting showing you how to define the setting and implement a 
function to process the data loaded from the feed.

## Filtering titles

The style and formatting of titles can vary markedly across different 
feeds. You can use this hook to tidy them up so they follow are similar
style.

```python
# myapp/settings.py
FEEDS_FILTER_TITLE = "myapp.utils.filter_title"
```

```python
# myapp/utils.py
import re

def filter_title(name: str) -> str:
    # Skip changes if the title is empty
    if not name:
        return name
    # Strip double-quotes around a title
    if name[0] == name[-1] == '"':
        name = name[1:-1]
    # Strip single-quotes around a title
    if name[0] == name[-1] == "'":
        name = name[1:-1]
    # Remove any trailing periods but leave an ellipsis alone
    if name[-1] == "." and name[-2] != ".":
        name = name[:-1]
    # Remove extra whitespace
    name = " ".join(name.split())
    # Put a space before and after a hyphen
    name = re.sub(r"(\w(\")?)-", r"\1 -", name)
    name = re.sub(r"-((\")?(\w))", r"- \1", name)
    # Put a space after a comma
    name = re.sub(r"(\w),(\w)", r"\1, \2", name)
    # Remove a space before a comma
    name = re.sub(r"(\w) ,", r"\1,", name)
    # Put a space before an opening bracket
    name = re.sub(r"(\w)\(", r"\1 (", name)
    # Put a space after a closing bracket
    name = re.sub(r"\)(\w)", r") \1", name)
    return name
```

## Filtering authors

When the list of authors for an entry in a feed is loaded any empty strings
are already filtered out, so this hook is less useful. However, given the way 
feeds are implemented it still might come in handy.

```python
# myapp/settings.py
FEEDS_FILTER_AUTHORS = "myapp.utils.filter_authors"
```

```python
# myapp/utils.py
from typing import List

def filter_authors(names: List[str]) -> List[str]:
    # remove any duplicates
    return list(set(names))
```

## Filtering tags

Filtering the list tags is almost always something you want to do. Many 
WordPress authors, for example, don't bother tagging their posts so the 
default "Uncategorized" tag is often the only one present. If you create 
a tag cloud, then this is likely something you want to filter out.

```python
# myapp/settings.py
FEEDS_FILTER_TAGS = "myapp.utils.filter_tags"
```

```python
# myapp/utils.py
from typing import List

def filter_tags(names: List[str]) -> List[str]:
     skip = ["uncategorized",]
     return [name for name in names if name.lower() not in skip]
```
