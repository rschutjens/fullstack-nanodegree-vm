#
# Database access functions for the web forum.
#

import time
import psycopg2
import bleach

## Database connection
DB = []

## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    pg = psycopg2.connect("dbname = forum")
    c = pg.cursor()
    c.execute("select content, time from posts order by time desc")
    DB = c.fetchall()
    pg.close()

    posts = [{'content': str(row[1]), 'time': str(row[0])} for row in DB]
    posts.sort(key=lambda row: row['time'], reverse=True)
    return posts

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
    pg = psycopg2.connect("dbname = forum")
    c = pg.cursor()
    #t = time.strftime('%c', time.localtime())

    c.execute("insert into posts (content) values (%s)", (bleach.clean(content), ))
    #DB.append((t, content))
    pg.commit()
    pg.close()
