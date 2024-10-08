from flask import Flask, render_template, jsonify, abort, request
from config import Config
from app.models import get_random_annotations, get_books_with_annotations, get_book_annotations, get_favorited_annotations, get_all_annotations, get_recent_books
from app.utils import is_favorite, toggle_favorite, to_datetime

app = Flask(__name__)
app.config.from_object(Config)
app.jinja_env.filters['to_datetime'] = to_datetime

@app.route('/', methods=['GET'])
def index():
    annotations = get_random_annotations()
    for annotation in annotations:
        annotation['is_favorite'] = is_favorite(annotation['id'])
    return render_template('index.html', annotations=annotations)

@app.route('/books', methods=['GET'])
def books_list():
    books = get_books_with_annotations()
    recent_books = get_recent_books()
    return render_template('books.html', recent_books=recent_books, books=books)

@app.route('/book/<int:book_id>', methods=['GET'])
def book_annotations(book_id):
    book_data = get_book_annotations(book_id)
    if book_data is None:
        abort(404)
    for annotation in book_data['annotations']:
        annotation['is_favorite'] = is_favorite(annotation['id'])
    return render_template('book.html', book_data=book_data)

@app.route('/toggle_favorite/<int:annotation_id>', methods=['POST'])
def toggle_favorite_route(annotation_id):
    success = toggle_favorite(annotation_id)
    return jsonify({"success": success})

@app.route('/favorites', methods=['GET'])
def favorites():
    favorited_annotations = get_favorited_annotations()
    return render_template('favorites.html', favorited_annotations=favorited_annotations)

@app.route('/focused', methods=['GET'])
def focused_view():
    book_id = request.args.get('book_id', type=int)
    index = request.args.get('index', 0, type=int)
    
    if book_id:
        book_data = get_book_annotations(book_id)
        if book_data is None:
            abort(404)
        annotations = book_data['annotations']
        book_title = book_data['title']
    else:
        annotations = get_all_annotations()
        book_title = annotations[index]['book_title']

    total = len(annotations)
    if index < 0:
        index = 0
    elif index >= total:
        index = total - 1

    current_annotation = annotations[index]
    current_annotation['is_favorite'] = is_favorite(current_annotation['id'])

    return render_template('focused.html', 
                           annotation=current_annotation, 
                           index=index, 
                           total=total, 
                           book_id=book_id,
                           book_title=book_title)