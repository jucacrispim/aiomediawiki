A simple asyncio wrapper to the MediaWiki API inspired by
[mediawiki](https://github.com/barrust/mediawiki).


Install
=======

```sh
$ pip install aiomediawiki
```

Usage
=====

```python
from aiomediawiki import MediaWiki

# You can change the language using the `lang` param.
# wiki = MediaWiki(lang='es')
# The default language is `en`.
wiki = MediaWiki()

# Search for pages
results = await wiki.search('python')
for page_title in results:
    print(page_title)

# Get a specific page
page = await wiki.get_page('Monty Python)
print(page.summary)

```

Notes
=====

Currently aiomedia wiki only has the search and get page features - the things
I was in need - but I intend to add more features when I have some free time.

Stay tuned!
