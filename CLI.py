from typing import Optional
import typer

from pymongo import MongoClient, DESCENDING
from pprint import pprint


# Provide the mongodb atlas url to connect python to mongodb using pymongo
CONNECTION_STRING = "mongodb+srv://altbalybalrhmn:CpnooyI6kvbUM7uz@freestudentcluster.kzvfjxb.mongodb.net/?retryWrites=true&w=majority"

# Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
client = MongoClient(CONNECTION_STRING)

# Get the database
db = client['Library']

print(db.client.list_database_names())
print(db.list_collection_names())
user_collection = db['users']
book_collection = db['books']


app = typer.Typer()


#####################################################################

# sign up
@app.command('signup')
def signup(user_name: str):

    try:
        user_collection.insert_one(
            {
                '_id': user_name,
                'history': {

                    'books_read': [],
                    'borrowing_now': [],
                    'fav_books': []
                }


            }
        )

    except:
        print('user name is already registered you can sign in now')
    else:
        print('registered successfully!')


########################################################################

# sign in
@app.command('signin')
def signin(user_name: str):

    try:
        results = user_collection.find_one({'_id': user_name})
        for i in results:
            print(f'your posts are {i}')
        print(f'welcome {user_name}. You are logged in')
    except:
        print('user not found sign up first')


########################################################################

# add a book
@app.command('add_book')
def add_book(book_id: int, book_name: str, genre: str, author: str):

    book_collection.insert_one({

        'book_id': book_id,
        'book_name': book_name,
        'genre': genre,
        'author': author,
        'status': "",
        'borrower': ''

    })
    print(f' {book_name} book was added successfully')


########################################################################

# borrow a book
@app.command('borrow_book')
def borrow_book(user_name: str, book_id: int):

    book_collection.update_one(
        {'status': ''}, {'$set': {'status': 'borrowed'}})
    book_collection.update_one(
        {'borrower': ''}, {'$set': {'borrower': user_name}})
    user_collection.update_one({'_id': user_name}, {
                               '$push': {'history.borrowing_now': book_id}})
    print(f' book with id {book_id} was borrowed by {user_name}')


############################################################

# return a book
@app.command('return_book')
def return_book(user_name: str, book_id: int):

    book_collection.update_one({'status': 'borrowed'}, {
                               '$set': {'status': ''}})
    book_collection.update_one({'borrower': user_name}, {
                               '$set': {'borrower': ''}})
    user_collection.update_one({'_id': user_name}, {
                               '$pull': {'history.borrowing_now': book_id}})
    user_collection.update_one({'_id': user_name}, {
                               '$push': {'history.books_read': book_id}})
    print(f' book with id {book_id} was returned by {user_name}')


###########################################################

# add favourit book
@app.command('add_favorite_book')
def add_favorite_book(user_name, book_id):
    user_collection.update_one(
        {'_id': user_name}, {'$push': {'history.fav_books': book_id}})
    print(
        f' book with id {book_id} was categorized as favourite by user {user_name}')


############################################################

# recently added n books
@app.command('recently_added')
def recently_added(n: int):
    select = {'$project': {'book_id': 1, 'book_name': 1}}
    all = {'$match': {}}  # filter
    sorted = {'$sort': {'_id': -1}}
    limited = {'$limit': n}

    results = book_collection.aggregate([all, select, sorted, limited])
    for result in results:
        print(result)


###############################################################

# search by book name
@app.command('search_name_book')
def search_name_book(book_name: str):
    filter = {
        '$match': {'book_name': book_name}
    }
    select = {'$project': {'book_id': 1, 'book_name': 1}}
    pipeline = [filter, select]
    results = book_collection.aggregate(pipeline)
    for result in results:
        print(result)

###################################################################

# search by author name


@app.command('search_author_book')
def search_author_book(author: str):

    filter = {
        '$match': {'author': author}
    }
    select = {'$project': {'book_id': 1, 'book_name': 1, 'author': 1}}
    pipeline = [filter, select]
    results = book_collection.aggregate(pipeline)
    for result in results:
        print(result)


###############################################################

# the most three readers
@app.command('book_read_count')
def book_read_count(n: int):
    stage_group_read_count_by_book_name = {
        "$group": {

            "_id": "$_id",
            "no_reads": {"$sum": {"$size": "$history.books_read"}
                         }}
    }

    stage_sort = {
        "$sort": {"no_reads": -1}
    }
    limit = {
        '$limit': n
    }
    pipeline = [stage_group_read_count_by_book_name, stage_sort, limit]

    results = user_collection.aggregate(pipeline)
    for result in results:
        print(result)

###############################################################

# most available genres


@app.command('most_available_genres')
def most_available_genres(n: int):
    group_stage = {
        '$group': {'_id': '$genre',
                   "no_books": {"$sum": 1}

                   }
    }

    stage_sort = {
        "$sort": {"no_books": -1}
    }
    limit = {
        '$limit': n
    }
    pipeline = [group_stage, stage_sort, limit]

    results = book_collection.aggregate(pipeline)
    for result in results:
        print(result)

####################################################################

# top_publishing_authors


@app.command('top_publisher_authors')
def top_publisher_authors(n):

    group_stage = {
        '$group': {'_id': '$author',
                   "no_books": {"$sum": 1}

                   }
    }

    stage_sort = {
        "$sort": {"no_books": -1}
    }
    limit = {
        '$limit': n
    }
    pipeline = [group_stage, stage_sort, limit]

    results = book_collection.aggregate(pipeline)
    for result in results:
        print(result)

#######################################################################
# user_statistics


@app.command('statistics')
def statistics():
    group_stage = {
        '$group': {'_id': '$_id',
                   'reads': {'$sum': {'$size': '$history.books_read'}},
                   'favourte': {'$sum': {'$size': '$history.fav_books'}},
                   'borrowing_now': {'$sum': {'$size': '$history.borrowing_now'}}
                   }
    }
    results = user_collection.aggregate([group_stage])
    for result in results:
        print(result)

###################################################
# end


if __name__ == "__main__":
    app()
