A simple asyncio wrapper to the MediaWiki API inspired by
[mediawiki](https://github.com/barrust/mediawiki).


Install
=======

```sh
$ pip install aiomediawiki
```

Usage
=====

Search
------

```python
from aiomediawiki import MediaWiki

# You can change the language using the `lang` param.
# wiki = MediaWiki(lang='es')
# The default language is `en`.
wiki = MediaWiki()

# Search for pages
results = await wiki.search('python')
async for page in results:
    print(page.title)
```

Using ``async for`` will load the pages as you iterate over it. To load
all pages at once use:

```python
results = await wiki.search('python')
await results.load_all()
for page in results:
    print(page.title)
```

Fetch
-----

```python
# Get a specific page
page = await wiki.get_page('Monty Python')
print(page.summary)

```

You can also fetch a page using its id

```python
page = await wiki.get_page(pageid=15954)
```

Notes
=====

Currently aiomedia wiki only has the search and get page features - the things
I was in need - but I intend to add more features when I have some free time.

Stay tuned!
