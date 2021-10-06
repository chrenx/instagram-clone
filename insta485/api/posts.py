"""REST API for posts."""
import uuid
import hashlib
import flask
import insta485


# Handle Exception, from Flask docs
class InvalidUsage(Exception):
    """API exception."""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Return rv."""
        show_message = dict(self.payload or ())
        show_message['message'] = self.message
        show_message['status_code'] = self.status_code
        return show_message


# Error Handler, from Flask docs
@insta485.app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Raise error."""
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# Use sha512 to process password with some salt
# Return: sha512$<salt>$<password_hash>
def get_processed_password(password, salt=uuid.uuid4().hex):
    """Generate a hashed password with some salt."""
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


# Check username and password credentials
def check_credentials(username, password):
    """Check username and password."""
    if not username or not password:
        raise InvalidUsage("Forbidden", 403)
    connection = insta485.model.get_db()
    password_db = connection.execute("SELECT password FROM users WHERE "
                                     "username = ?", (username,))
    # check if username or password exists
    cur = password_db.fetchone()
    if cur is None:
        raise InvalidUsage("Forbidden", 403)
    password_list = cur["password"].split("$")
    salt_origin_db = password_list[1]
    password_hash_input = get_processed_password(password, salt_origin_db)

    # sha512$<salt>$<password_hash>
    if password_hash_input != cur["password"]:
        # authentication fails
        raise InvalidUsage("Forbidden", 403)


def get_posts_results(username, postid_lte, size, page):
    """Find all posts related."""
    next_url = ""
    results = []
    connection = insta485.model.get_db()
    offset = size * page

    # find all realted persons
    cur = connection.execute(
        "SELECT username2 FROM following WHERE username1=?",
        (username,)
    )
    cur = cur.fetchall()
    all_people = [name["username2"] for name in cur]
    all_people.append(username)

    # find all related posts, and check if it fullfills the page
    all_people = tuple(all_people)
    cur = connection.execute(
        f"SELECT * FROM posts "
        f"LEFT JOIN users ON posts.owner=users.username "
        f"WHERE posts.owner IN {all_people} "
        f"ORDER BY postid DESC "
        f"LIMIT {size} OFFSET {offset}"
    )
    cur = cur.fetchall()
    if len(cur) >= size:
        # there should be url for next
        new_postid_lte = postid_lte
        if postid_lte is None:
            new_postid_lte = cur[0]["postid"]
        next_url += (flask.request.path + "?size=" + str(size) + "&page=" +\
                     str(page + 1) + "&postid_lte=" + str(new_postid_lte))
    
    # process the results
    for post in cur:
        # add comments to results
        sub_result = {}
        comments = []
        cur2 = connection.execute(
            "SELECT * FROM comments WHERE postid=? ORDER BY commentid",
            (post["postid"],)
        )
        cur2 = cur2.fetchall()
        for comment in cur2:
            sub_comment = {}
            sub_comment["commentid"] = comment["commentid"]
            sub_comment["lognameOwnsThis"] = username == comment["owner"]
            # if username != comment["owner"]:
            #     sub_comment["lognameOwnsThis"] = "false"
            sub_comment["owner"] = comment["owner"]
            sub_comment["ownerShowUrl"] = "/users/" + comment["owner"] + "/"
            sub_comment["text"] = comment["text"]
            sub_comment["url"] = "/api/v1/comments/" +\
                                 str(comment["commentid"]) + "/"
            comments.append(sub_comment)
        sub_result["comments"] = comments
        results.append(sub_result)

    return results, next_url


@insta485.app.route("/api/v1/posts/")
def get_apiv1_posts():
    """Return the 10 newest posts."""
    username = ""
    password = ""
    if "logname" not in flask.session:
        if flask.request.authorization is None:
            raise InvalidUsage("Forbidden", 403)
        username = flask.request.authorization["username"]
        password = flask.request.authorization["password"]
        check_credentials(username, password)
        # credential passed
    else:
        username = flask.session["logname"]

    url = flask.request.full_path
    if flask.request.args.get("size") is None and \
        flask.request.args.get("page") is None and \
        flask.request.args.get("postid_lte") is None:
        url = flask.request.path
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    postid_lte = flask.request.args.get("postid_lte", type=int)
    if size < 0 or page < 0:
        # size & page must be non-negative integers
        raise InvalidUsage("Bad Request", 400)

    results, next_url = get_posts_results(username, postid_lte, size, page)

    context = {
      "next": next_url,
      "results": results,
      "url": url
    }

    return flask.jsonify(**context)


@insta485.app.route("/api/v1/")
def get_apiv1():
    """Return a list of services available."""
    context = {
      "comments": "/api/v1/comments/",
      "likes": "/api/v1/likes/",
      "posts": "/api/v1/posts/",
      "url": "/api/v1/"
    }
    return flask.jsonify(**context)


@insta485.app.route("/api/v1/posts/<int:postid_url_slug>/")
def get_post(postid_url_slug):
    """Return post on postid."""
    context = {
        "age": "2017-09-28 04:33:28",
        "img_url": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
        "owner": "awdeorio",
        "owner_img_url": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
        "owner_show_url": "/users/awdeorio/",
        "postid": "/posts/{}/".format(postid_url_slug),
        "url": flask.request.path,
    }
    return flask.jsonify(**context)
