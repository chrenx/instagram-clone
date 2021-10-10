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


# Check authorization, return username
def check_authorization():
    """Helper function to check authorization."""
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
    return username


def get_all_comments(post, username):
    """Get comments for the post."""
    comments = []
    connection = insta485.model.get_db()
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
    return comments


def get_all_likes(post, username):
    """Get all likes for the post."""
    likes = {}
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM likes WHERE postid=?", (post["postid"],)
    )
    cur = cur.fetchall()
    num_likes = len(cur)
    like_or_not = connection.execute(
        "SELECT * FROM likes WHERE postid=? AND owner=?",
        (post["postid"], username,)
    )
    like_or_not = like_or_not.fetchone()
    likes["lognameLikesThis"] = like_or_not is not None
    likes["numLikes"] = num_likes
    url = None
    if like_or_not is not None:
        # logname like this post, then find the row number of his/her like
        cur = connection.execute(
            "WITH mytable AS "
            "( "
            "SELECT postid, owner, ROW_NUMBER() OVER() AS rownum FROM likes "
            ") "
            "SELECT rownum FROM mytable WHERE postid=? AND owner=?",
            (post["postid"], username,)
        )
        cur = cur.fetchone()
        row_num = cur["rownum"]
        url = "/api/v1/likes/" + str(row_num) + "/"
    likes["url"] = url
    return likes


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
    if postid_lte is None:
        cur = connection.execute(
            f"SELECT posts.postid AS postid, posts.filename AS postsFilename, "
            f"posts.owner AS owner, posts.created AS created, "
            f"users.filename AS usersFilename "
            f"FROM posts "
            f"LEFT JOIN users ON posts.owner=users.username "
            f"WHERE posts.owner IN {all_people} "
            f"ORDER BY postid DESC "
            f"LIMIT {size} OFFSET {offset}"
        )
    else:
        cur = connection.execute(
            f"SELECT posts.postid AS postid, posts.filename AS postsFilename, "
            f"posts.owner AS owner, posts.created AS created, "
            f"users.filename AS usersFilename "
            f"FROM posts "
            f"LEFT JOIN users ON posts.owner=users.username "
            f"WHERE posts.owner IN {all_people} "
            f"AND posts.postid<={postid_lte} "
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
        sub_result["comments"] = get_all_comments(post, username)
        sub_result["created"] = post["created"]
        sub_result["imgUrl"] = "/uploads/" + post["postsFilename"]
        sub_result["likes"] = get_all_likes(post, username)
        sub_result["owner"] = post["owner"]
        sub_result["ownerImgUrl"] = "/uploads/" + post["usersFilename"]
        sub_result["ownerShowUrl"] = "/users/" + post["owner"] + "/"
        sub_result["postShowUrl"] = "/posts/" + str(post["postid"]) + "/"
        sub_result["postid"] = post["postid"]
        sub_result["url"] = "/api/v1/posts/" + str(post["postid"]) + "/"
        results.append(sub_result)

    return results, next_url


def get_query_url():
    """Get the url of query."""
    url = flask.request.full_path
    if flask.request.args.get("size") is None and \
        flask.request.args.get("page") is None and \
        flask.request.args.get("postid_lte") is None:
        url = flask.request.path
    return url


@insta485.app.route("/api/v1/comments/<int:commentid>/", methods=["DELETE"])
def delete_comment(commentid):
    """Detele a comment."""
    username = check_authorization()
    if flask.request.method != "DELETE":
        return None
    if commentid is None:
        raise InvalidUsage("Bad Request", 400)
    connection = insta485.model.get_db()
    connection.execute(
        "DELETE FROM comments WHERE owner=? AND commentid=?",
        (username, commentid,)
    )
    return "", 204


@insta485.app.route("/api/v1/comments/", methods=["POST"])
def add_comment():
    """Add a new comment."""
    username = check_authorization()
    if flask.request.method != "POST":
        return None
    postid = flask.request.args.get("postid", type=int)
    if postid is None:
        raise InvalidUsage("Bad Request", 400)
    data = flask.request.get_json(force=True)
    comment = data['text']
    connection = insta485.model.get_db()
    connection.execute(
        "INSERT INTO comments(owner, postid, text) "
        "VALUES (?, ?, ?)",
        (username, postid, comment,)
    )
    cur = connection.execute(
        "SELECT last_insert_rowid() AS commentid FROM comments"
    )
    cur = cur.fetchone()
    commentid = cur["commentid"]
    context = {
        "commentid": commentid,
        "lognameOwnsThis": True,
        "owner": username,
        "ownerShowUrl": "/users/" + username + "/",
        "text": comment,
        "url": "/api/v1/comments/" + str(commentid)
    }
    return flask.jsonify(**context), 201


@insta485.app.route("/api/v1/likes/<int:likeid>/", methods=["DELETE"])
def delete_like(likeid):
    """Create one like for a specific post."""
    username = check_authorization()
    if flask.request.method != "DELETE":
        return None
    if likeid is None:
        raise InvalidUsage("Bad Request", 400)
    connection = insta485.model.get_db()
    connection.execute(
        "DELETE FROM likes WHERE owner=? AND likeid=?",
        (username, likeid,)
    )
    return "", 204


@insta485.app.route("/api/v1/likes/", methods=["POST"])
def create_like():
    """Create one like for a specific post."""
    username = check_authorization()
    if flask.request.method != "POST":
        return None
    postid = flask.request.args.get("postid", type=int)
    if postid is None:
        raise InvalidUsage("Bad Request", 400)
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM likes WHERE postid=? AND owner=?",
        (postid, username,)
    )
    cur = cur.fetchone()
    if cur is not None:
        raise InvalidUsage("Conflict xx " + str(cur["likeid"]), 409)
    # create a like now
    connection.execute(
        "INSERT INTO likes(owner, postid) "
        "VALUES (?, ?)",
        (username, postid,)
    )
    cur = connection.execute(
        "SELECT likeid FROM likes WHERE owner=? AND postid=?",
        (username, postid,)
    )
    cur = cur.fetchone()
    likeid = cur["likeid"]
    url = "/api/v1/likes/" + str(likeid) + "/"
    context = {
        "likeid": likeid,
        "url": url
    }
    return flask.jsonify(**context), 201


@insta485.app.route("/api/v1/posts/<int:postid>/")
def get_apiv1_posts_detail(postid):
    """Get the details of a post."""
    username = check_authorization()
    context = {}
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT posts.postid AS postid, posts.filename AS postsFilename, "
        "posts.owner AS owner, posts.created AS created, "
        "users.filename AS usersFilename "
        "FROM posts "
        "LEFT JOIN users ON posts.owner=users.username "
        "WHERE posts.postid=?",
        (postid,)
    )
    cur = cur.fetchone()
    # check if such post exists
    if cur is None:
        raise InvalidUsage("Not Exist", 404)
    context["comments"] = get_all_comments(cur, username)
    context["created"] = cur["created"]
    context["imgUrl"] = "/uploads/" + cur["postsFilename"]
    context["likes"] = get_all_likes(cur, username)
    context["owner"] = cur["owner"]
    context["ownerImgUrl"] = "/uploads/" + cur["usersFilename"]
    context["ownerShowUrl"] = "/users/" + cur["owner"] + "/"
    context["postShowUrl"] = "/posts/" + str(cur["postid"]) + "/"
    context["postid"] = cur["postid"]
    context["url"] = "/api/v1/posts/" + str(cur["postid"]) + "/"

    return flask.jsonify(**context)


@insta485.app.route("/api/v1/posts/")
def get_apiv1_posts():
    """Return the 10 newest posts."""
    username = check_authorization()

    url = get_query_url()
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
