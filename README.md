# calebcc: python blog engine

This project is the engine that drives my blog at [calebbrown.id.au](http:\\calebbrown.id.au).

## Overview

This blog is powered by a static JSON database stored on disk rather than using a more traditional relational database.
The JSON database is populated from Markdown, HTML or text formated source files.

The website is built using the Python micro web framework, [Bottle](http://bottlepy.org/) with memcached being used to reduce disk access.

The frontend layout is built using [Bootstrap](http://twitter.github.io/bootstrap/).

## Quick Start

**Warning:** this project is currently designed to only run my blog so your milage may vary

#### 1. Get the source

Using git:

    $ git clone git://github.com/calebbrown/calebcc.git

Or download [the zip file](https://github.com/calebbrown/calebcc/archive/master.zip)


#### 2. Install dependencies using pip

Inside a virutal environment run:

    $ cd calebcc
    $ pip -r requirements.txt

#### 3. Create some source files

Create the source directory structure.

    $ mkdir -p source_data/pages
    $ mkdir -p source_data/blog
    $ mkdir -p source_data/media
    $ mkdir -p source_data/legacy

In `source_data/pages` create a page named `about.md` with the following content:

    Title: About

    # This is the about page

In `source_data/blog` create a page named `hello.md` with the following content:

    Title: Gabriel Marshall Brown
    Date: Tue, 07 May 2013 20:44:00 +1100
    Author: Joe Blogs
    Channel: life

    Hello, World!


#### 4. Update the development environment config

Open up `env/dev.py` in an editor and add the following lines:

    DATA_SOURCE = '/path/to/calebcc/source_data'
    DATA_STORE = '/path/to/calebcc/compiled_data'

#### 4. Generate the JSON database

We have some data and have updated the config so we can build the database:

    $ python calebcc.py --parse
    Parsing docs...
    $


#### 5. Run the webserver

Now we're ready to go - time to run the server:

    $ python calebcc.py
    Bottle server starting up (using WSGIRefServer())...
    Listening on http://localhost:8080/
    Hit Ctrl-C to quit.

To view the website visit [localhost:8080](http://localhost:8080/) in a browser!

## Source Format

The blog engine parses documents based on text files with email message formated headers and a body of Markdown, HTML or raw text.

For example in `first.md` we might have:

    Title: First Post!
    Author: Joe Blogs
    Date: Tue, 07 May 2013 20:44:00 +1100

    # First Post

    This is the first post

In this example we have a markdown formatted post with the title "First Post!", written by "Joe Blogs". The filename is used to define the *url* of the post
and the format of the text.

It is also possible to specify the format using the `Format` header. Apart from `markdown`, `html` and `text` are supported.

A blank line is required between the last header and the first line of the body.

#### Creating Alternative URLs

The  header `Alt-Slug` can be added to indicate an alternative location for the document to be accessed under. This is particularly useful in the case where
a blog post has been renamed.

When a user visits the alternative location they are redirected to the real location.

Multiple `Alt-Slug` headers can be added for multiple redirects.


