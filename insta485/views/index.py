"""
Insta485 index (main) view.

URLs include:
/
"""

import pathlib
import uuid
import hashlib
import os
import arrow
import flask
import insta485


# Static file permission:
@insta485.app.route("/uploads/<filename>")
def static_permission(filename):
    """File access."""
    if "logname" not in flask.session:
        flask.abort(403)
    # check if file exists
    if not os.path.exists(os.path.join(insta485.app.config["UPLOAD_FOLDER"],
                          filename)):
        flask.abort(404)
    return flask.send_from_directory(insta485.app.config["UPLOAD_FOLDER"],
                                     filename, as_attachment=True)


# Use sha512 to process password with some salt
def get_processed_password(password, salt=uuid.uuid4().hex):
    """Generate a hashed password with some salt."""
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


# Both cannot be empty
# Password in the form of: sha512$<salt>$<password_hash>
# If authentification succeeds, it creates a session
def authentication():
    """Check username and password authentication."""
    username_in = flask.request.form["username"]
    password_in = flask.request.form["password"]
    # username or password fields are empty
    if not username_in or not password_in:
        flask.abort(400)
    connection = insta485.model.get_db()
    password_db = connection.execute("SELECT password FROM users WHERE "
                                     "username = ?", (username_in,))
    # check if username or password exists
    cur = password_db.fetchone()
    if cur is None:
        flask.abort(403)
    password_list = cur["password"].split("$")
    salt_origin_db = password_list[1]
    password_hash_input = get_processed_password(password_in, salt_origin_db)
    if password_hash_input == cur["password"]:  # sha512$<salt>$<password_hash>
        # authentication succeeded
        flask.session["logname"] = username_in
    else:
        flask.abort(403)


# Create a new account
def create_account():
    """Create a new account."""
    fullname_in = flask.request.form["fullname"]
    username_in = flask.request.form["username"]
    email_in = flask.request.form["email"]
    password_in = flask.request.form["password"]

    if "file" not in flask.request.files or not fullname_in or \
       not username_in or not email_in or not password_in:
        # error
        flask.abort(400)

    connection = insta485.model.get_db()
    cur = connection.execute("SELECT 1 FROM users WHERE username = ?",
                             (username_in,))
    if len(cur.fetchall()) == 1:
        # conflict on username
        flask.abort(409)

    # Unpack flask object
    file_in = flask.request.files["file"]
    file_name = file_in.filename

    # Compute base name (filename without directory).  We use a UUID to avoid
    # clashes with existing files, and ensure that the name is compatible with
    # the filesystem.
    uuid_basename = f"{uuid.uuid4().hex}{pathlib.Path(file_name).suffix}"

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    file_in.save(path)
    encrypt = get_processed_password(password_in)

    connection.execute("INSERT INTO users(username, fullname, email, filename,"
                       " password) VALUES (?, ?, ?, ?, ?)",
                       (username_in, fullname_in, email_in,
                        uuid_basename, encrypt,))
    flask.session["logname"] = username_in


def humanize_time(created):
    """Humanize the date."""
    arrow.get(created)
    utc = arrow.utcnow()
    local = utc.to('US/Pacific')
    return local.humanize()


def delete_account():
    """Delete a account."""
    logname = flask.session["logname"]
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT filename FROM users WHERE username=?", (logname,)
    )
    cur = cur.fetchone()
    profile = cur["filename"]
    os.remove(os.path.join(insta485.app.config["UPLOAD_FOLDER"], profile))
    cur = connection.execute(
        "SELECT filename FROM posts WHERE owner=?", (logname,)
    )
    all_posts = cur.fetchall()
    for pic in all_posts:
        os.remove(os.path.join(insta485.app.config["UPLOAD_FOLDER"],
                  pic["filename"]))
        print("删了！！！！！！")
    connection.execute(
        "DELETE FROM users WHERE username=?", (logname,)
    )


def edit_account():
    """Edit a account."""
    logname = flask.session["logname"]
    email = flask.request.form["email"]
    fullname = flask.request.form["fullname"]

    if not fullname or not email:
        # error
        flask.abort(400)

    # Unpack flask object
    file_in = flask.request.files["file"]
    file_name = file_in.filename

    # Compute base name (filename without directory).  We use a UUID to avoid
    # clashes with existing files, and ensure that the name is compatible with
    # the filesystem.
    uuid_basename = f"{uuid.uuid4().hex}{pathlib.Path(file_name).suffix}"

    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    file_in.save(path)

    connection = insta485.model.get_db()
    # delete olf file
    cur = connection.execute(
        "SELECT filename FROM users WHERE username=?", (logname,)
    )
    cur = cur.fetchone()
    file_old = cur["filename"]
    os.remove(os.path.join(insta485.app.config["UPLOAD_FOLDER"], file_old))

    connection.execute(
        "UPDATE users SET fullname=?, email=?, filename=? WHERE username=?",
        (fullname, email, uuid_basename, logname,)
    )


def update_password():
    """Update."""
    username = flask.session["logname"]
    password = flask.request.form["password"]
    new_password1 = flask.request.form["new_password1"]
    new_password2 = flask.request.form["new_password2"]
    if not password or not new_password1 or not new_password2:
        flask.abort(400)

    connection = insta485.model.get_db()
    password_db = connection.execute("SELECT password FROM users WHERE "
                                     "username = ?", (username,))
    # check if username or password exists
    cur = password_db.fetchone()
    if cur is None:
        flask.abort(403)
    password_list = cur["password"].split("$")
    salt_origin_db = password_list[1]
    password_hash_input = get_processed_password(password, salt_origin_db)
    if password_hash_input != cur["password"]:  # sha512$<salt>$<password_hash>
        # authentication fail
        flask.abort(403)
    if new_password1 != new_password2:
        flask.abort(401)
    hash_new_password = get_processed_password(new_password1)
    connection.execute(
        "UPDATE users SET password=? WHERE username=?",
        (hash_new_password, username,)
    )


# IMPORTANT: user1 is logname, user2 is logname's following
@insta485.app.route('/')
def show_index():
    """Display / route."""
    # check if account is logged in
    if "logname" in flask.session:
        # Connect to database
        connection = insta485.model.get_db()
        # logname = flask.session["logname"]
        # Query database

        # get all posts
        cur = connection.execute(
            "SELECT * FROM posts WHERE owner=?",
            (flask.session["logname"],)
        )
        row = cur.fetchone()  # a list of dictionary
        all_posts = []  # [(postid, filename, owner, created), (...), ..]
        # add logname's posts
        while row is not None:
            all_posts.append((row["postid"], row["filename"],
                              row["owner"], humanize_time(row["created"])))
            row = cur.fetchone()

        all_profiles = {}
        # add logname's profile
        cur = connection.execute(
            "SELECT filename FROM users WHERE username=?",
            (flask.session["logname"],)
        )
        cur = cur.fetchone()
        all_profiles[flask.session["logname"]] = cur["filename"]

        # get all logname's following
        cur = connection.execute(
            "SELECT * FROM following WHERE username1=?",
            (flask.session["logname"],)
        )

        followings = cur.fetchall()

        for token in followings:
            following1 = token["username2"]
            # get profile picture name
            cur = connection.execute(
                "SELECT filename FROM users WHERE username=?",
                (following1,)
            )
            cur = cur.fetchone()
            all_profiles[following1] = cur["filename"]

            cur = connection.execute(
                "SELECT * FROM posts WHERE owner=?",
                (following1,)
            )
            row = cur.fetchone()
            while row is not None:
                all_posts.append((row["postid"], row["filename"],
                                  row["owner"], humanize_time(row["created"])))
                row = cur.fetchone()
        # sort all posts according to postid in descending order
        all_posts = sorted(all_posts, key=lambda post: post[0], reverse=True)

        all_likes = {}
        all_comments = {}
        like_it = {}
        for post in all_posts:
            cur = connection.execute(
                "SELECT * FROM likes WHERE postid=?",
                (post[0],)
            )
            like = cur.fetchall()
            all_likes[post[0]] = len(like)

            # check wether the logname likes this post
            cur = connection.execute(
                "SELECT likeid FROM likes WHERE postid=? AND owner=?",
                (post[0], flask.session["logname"],)
            )
            cur = cur.fetchone()
            if cur is not None:
                # logname likes it
                like_it[post[0]] = True
            else:
                like_it[post[0]] = False

            # add comment
            cur = connection.execute(
                "SELECT * FROM comments WHERE postid=?",
                (post[0],)
            )
            row = cur.fetchone()
            current_post = []  # list of tuples
            while row is not None:
                current_post.append((row["commentid"], row["owner"],
                                     row["text"]))
                row = cur.fetchone()
            current_post = sorted(current_post, key=lambda curr: curr[0],
                                  reverse=True)
            all_comments[post[0]] = current_post

        # Add database info to context
        # all_posts: [(postid, filename, owner, created), (...), ..]
        # likes: {postid: #likes}
        # comment: {postid:[(comment1, owner, text), ... ]}
        # profiles: {name:filename}
        # like_this_post: {postid:true/false}
        context = {
            "logname": flask.session["logname"],
            "posts": all_posts,
            "likes": all_likes,
            "comments": all_comments,
            "profiles": all_profiles,
            "current_page": flask.request.path,
            "like_this_post": like_it
        }

        # Here the **context is a kwargs: context.item()
        return flask.render_template("index.html", **context)
    return flask.redirect(flask.url_for("login"))


@insta485.app.route("/accounts/password/")
def change_password():
    """Delete."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login"))
    # if flask.request.method == "POST":
    #     return flask.redirect(flask.url_for("show_index"))
    return flask.render_template("password.html",
                                 logname=flask.session["logname"])


@insta485.app.route("/posts/<string:postid_url_slug>/")
def posts(postid_url_slug):
    """Post."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    logname = flask.session["logname"]

    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT owner FROM posts WHERE postid=?", (postid_url_slug,)
    )
    cur = cur.fetchone()
    owner = cur["owner"]

    cur = connection.execute(
        "SELECT filename FROM users WHERE username=?", (owner,)
    )
    cur = cur.fetchone()
    owner_img = cur["filename"]

    cur = connection.execute(
        "SELECT filename FROM posts WHERE postid=?", (postid_url_slug,)
    )
    cur = cur.fetchone()
    post_img = cur["filename"]

    cur = connection.execute(
        "SELECT created FROM posts WHERE postid=?", (postid_url_slug,)
    )
    cur = cur.fetchone()
    timestamp = humanize_time(cur["created"])

    cur = connection.execute(
        "SELECT * FROM likes WHERE postid=?", (postid_url_slug,)
    )
    cur = cur.fetchall()
    num_like = len(cur)

    cur = connection.execute(
        "SELECT * FROM comments WHERE postid=?", (postid_url_slug,)
    )
    cur = cur.fetchall()
    all_comments = []
    for token in cur:
        all_comments.append((token["commentid"], token["owner"],
                             token["text"]))

    cur = connection.execute(
        "SELECT * FROM likes WHERE postid=? AND owner=?",
        (postid_url_slug, logname)
    )
    cur = cur.fetchone()
    like_already = False
    if cur is not None:
        # logname likes it
        like_already = True

    content = {
        "logname": logname,
        "owner": owner,
        "owner_img": owner_img,
        "post_img": post_img,
        "current_page": flask.request.path,
        "postid": postid_url_slug,
        "timestamp": timestamp,
        "likes": num_like,
        "comments": all_comments,
        "like_already": like_already
    }

    return flask.render_template("post.html", **content)


@insta485.app.route("/users/<user_url_slug1>/followers/")
def follower(user_url_slug1):
    """Follower."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    logname = flask.session["logname"]

    connection = insta485.model.get_db()

    # check user_url_slug exists
    cur = connection.execute(
        "SELECT * FROM users WHERE username=?", (user_url_slug1,)
    )
    if cur.fetchone() is None:
        flask.abort(404)

    cur = connection.execute(
        "SELECT * FROM following WHERE username2=?", (user_url_slug1,)
    )
    all_followers = []
    row = cur.fetchone()
    while row is not None:
        all_followers.append(row["username1"])
        row = cur.fetchone()

    followers_info = []
    for follow in all_followers:
        cur = connection.execute(
            "SELECT filename FROM users WHERE username=?", (follow,)
        )
        filename = cur.fetchone()

        cur = connection.execute(
            "SELECT * FROM following WHERE username1=? AND username2=?",
            (logname, follow,)
        )
        cur = cur.fetchone()
        if cur is None:
            followers_info.append((follow, filename["filename"], False))
        else:
            followers_info.append((follow, filename["filename"], True))

    content = {
        "logname": logname,
        "followers": followers_info,
        "current_page": flask.request.path
    }

    return flask.render_template("followers.html", **content)


@insta485.app.route("/users/<string:user_url_slug2>/following/")
def following(user_url_slug2):
    """Following."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    logname = flask.session["logname"]

    connection = insta485.model.get_db()

    # check user_url_slug exists
    cur = connection.execute(
        "SELECT * FROM users WHERE username=?", (user_url_slug2,)
    )
    if cur.fetchone() is None:
        flask.abort(404)

    cur = connection.execute(
        "SELECT * FROM following WHERE username1=?", (user_url_slug2,)
    )
    all_followings = []
    row = cur.fetchone()
    while row is not None:
        all_followings.append(row["username2"])
        row = cur.fetchone()

    following_info = []
    for follow in all_followings:
        cur = connection.execute(
            "SELECT filename FROM users WHERE username=?", (follow,)
        )
        filename = cur.fetchone()

        cur = connection.execute(
            "SELECT * FROM following WHERE username1=? AND username2=?",
            (logname, follow,)
        )
        cur = cur.fetchone()
        if cur is None:
            following_info.append((follow, filename["filename"], False))
        else:
            following_info.append((follow, filename["filename"], True))

    content = {
        "logname": logname,
        "following": following_info,
        "current_page": flask.request.path
    }

    return flask.render_template("following.html", **content)


@insta485.app.route("/users/<string:user_url_slug>/")
def users(user_url_slug):
    """Users."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    logname = flask.session["logname"]

    connection = insta485.model.get_db()

    # check user_url_slug exists
    cur = connection.execute(
        "SELECT * FROM users WHERE username=?", (user_url_slug,)
    )
    if cur.fetchone() is None:
        flask.abort(404)

    # get number of posts
    cur = connection.execute(
        "SELECT * FROM posts WHERE owner=?", (user_url_slug,)
    )
    num_posts = len(cur.fetchall())
    # get postid and picture
    all_posts = []
    cur = connection.execute(
        "SELECT * FROM posts WHERE owner=?",
        (user_url_slug,)
    )
    row = cur.fetchone()  # a list of dictionary
    # [(postid, filename, owner, created), (...), ..]
    # add logname's posts
    while row is not None:
        all_posts.append((row["postid"], row["filename"],
                         row["owner"], humanize_time(row["created"])))
        row = cur.fetchone()

    # get number of num_followings
    cur = connection.execute(
        "SELECT * FROM following WHERE username1=?", (user_url_slug,)
    )
    num_followings = len(cur.fetchall())
    # get number of num_followers
    cur = connection.execute(
        "SELECT * FROM following WHERE username2=?", (user_url_slug,)
    )
    num_followers = len(cur.fetchall())
    # get fullname
    cur = connection.execute(
        "SELECT fullname FROM users WHERE username=?", (user_url_slug,)
    )
    fullname = cur.fetchone()
    fullname = fullname["fullname"]

    # check if logname follows username
    check_follow = False
    if logname != user_url_slug:
        cur = connection.execute(
            "SELECT * FROM following WHERE username1=? AND username2=?",
            (logname, user_url_slug,)
        )
        if cur.fetchone() is not None:
            check_follow = True

    content = {
        "logname": logname,
        "username": user_url_slug,
        "num_posts": num_posts,
        "num_followers": num_followers,
        "num_followings": num_followings,
        "fullname": fullname,
        "posts": all_posts,
        "current_page": flask.request.path,
        "logname_follows_username": check_follow
    }

    return flask.render_template("user.html", **content)


@insta485.app.route("/explore/")
def explore():
    """Explore."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    logname = flask.session["logname"]

    connection = insta485.model.get_db()

    # find all unfollow people
    cur = connection.execute(
        "SELECT * FROM users"
    )
    cur = cur.fetchall()
    all_users = []
    for token in cur:
        if token["username"] != logname:
            all_users.append((token["username"], token["filename"]))
    unfollow = []
    for usr in all_users:
        cur = connection.execute(
            "SELECT * FROM following WHERE username1=? AND username2=?",
            (logname, usr[0])
        )
        if cur.fetchone() is None:
            unfollow.append(usr)

    content = {
        "logname": logname,
        "current_page": flask.request.path,
        "unfollow": unfollow
    }

    return flask.render_template("explore.html", **content)


@insta485.app.route("/accounts/delete/")
def delete():
    """Delete."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login"))
    # if flask.request.method == "POST":
    #     return flask.redirect(flask.url_for("show_index"))
    return flask.render_template("delete.html",
                                 logname=flask.session["logname"])


@insta485.app.route("/accounts/edit/")
def edit():
    """Edit account."""
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login"))
    logname = flask.session["logname"]

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM users WHERE username=?", (logname,)
    )
    cur = cur.fetchone()
    fullname = cur["fullname"]
    email = cur["email"]
    profile = cur["filename"]

    content = {
        "logname": logname,
        "fullname": fullname,
        "email": email,
        "profile": profile,
        "current_page": flask.request.path
    }

    return flask.render_template("edit.html", **content)


@insta485.app.route("/accounts/login/")
def login():
    """Login."""
    # if flask.request.method == "POST":
    #     return flask.redirect(flask.url_for("show_index"))
    if "logname" in flask.session:
        return flask.redirect(flask.url_for("show_index"))
    return flask.render_template("login.html")


@insta485.app.route("/accounts/create/")
def sign_up():
    """Sign up for a new user."""
    if "logname" in flask.session:
        return flask.redirect(flask.url_for("edit"))
    return flask.render_template("create.html")


@insta485.app.route("/following/", methods=["POST"])
def act_follow():
    """Following."""
    if flask.request.method != "POST":
        return None

    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    logname = flask.session["logname"]
    username = flask.request.form["username"]
    operation = flask.request.form["operation"]
    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT * FROM following WHERE username1=? AND username2=?",
        (logname, username,)
    )
    cur = cur.fetchone()
    check_follow = True
    if cur is None:
        check_follow = False

    if operation == "follow":
        if check_follow:
            flask.abort(409)
        connection.execute(
            "INSERT INTO following(username1, username2) VALUES "
            "(?, ?)", (logname, username,)
        )
    if operation == "unfollow":
        if not check_follow:
            flask.abort(409)
        connection.execute(
            "DELETE FROM following where username1=? AND username2=?",
            (logname, username,)
        )

    target = flask.request.args.get("target")
    if target is None or target == "/":
        return flask.redirect("/")
    return flask.redirect(target)


# This function operates on login checking, account creating & editing
@insta485.app.route("/accounts/", methods=["POST"])
def accounts():
    """Operating accounts."""
    if flask.request.method != "POST":
        return None
    # Get operation: login, create, delete, edit_account
    operation = flask.request.form["operation"]

    # login operation
    if operation == "login":
        authentication()

    # create operation
    if operation == "create":
        create_account()

    # delete operation
    if operation == "delete":
        if "logname" not in flask.session:
            flask.abort(403)
        delete_account()
        flask.session.clear()

    # edit account
    if operation == "edit_account":
        if "logname" not in flask.session:
            flask.abort(403)
        edit_account()

    # update password
    if operation == "update_password":
        if "logname" not in flask.session:
            flask.abort(403)
        update_password()

    target = flask.request.args.get("target")
    if target is None or target == "/":
        return flask.redirect("/")
    return flask.redirect(target)


@insta485.app.route("/posts/", methods=["POST"])
def deal_posts():
    """Post."""
    if flask.request.method != "POST":
        return None
    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login"))
    logname = flask.session["logname"]
    operation = flask.request.form["operation"]
    connection = insta485.model.get_db()

    if operation == "create":
        # Unpack flask object
        file_in = flask.request.files["file"]
        file_name = file_in.filename

        uuid_basename = f"{uuid.uuid4().hex}{pathlib.Path(file_name).suffix}"

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        file_in.save(path)
        if os.stat(path).st_size == 0:
            path.unlink()
            flask.abort(400)
        connection.execute(
            "INSERT INTO posts(filename, owner) VALUES (?, ?)",
            (uuid_basename, logname,)
        )

    if operation == "delete":
        postid = flask.request.form["postid"]
        cur = connection.execute(
            "SELECT * FROM posts WHERE postid=? AND owner=?",
            (postid, logname)
        )
        data = cur.fetchone()
        if data is None:
            flask.abort(403)

        os.remove(os.path.join(insta485.app.config["UPLOAD_FOLDER"],
                               data["filename"]))
        connection.execute(
            "DELETE FROM posts WHERE postid=? AND owner=?", (postid, logname)
        )

    target = flask.request.args.get("target")
    if target is None:
        return flask.redirect(flask.url_for("users", user_url_slug=logname))
    return flask.redirect(target)


# Deal with POST likes
@insta485.app.route("/likes/", methods=["POST"])
def likes():
    """Deal with POST likes."""
    if flask.request.method != "POST":
        return None

    if "logname" in flask.session:
        operation = flask.request.form["operation"]
        postid = flask.request.form["postid"]

        connection = insta485.model.get_db()
        username = flask.session["logname"]

        # check if like or unlike already existed
        cur = connection.execute("SELECT * FROM likes WHERE "
                                 "postid=? AND owner = ?",
                                 (postid, username,))

        check_like = cur.fetchone()

        cur = connection.execute("SELECT * FROM likes")
        print(cur.fetchall())

        if operation == "like":
            # create a like for postid
            # check if a like is already existed
            if check_like is not None:
                flask.abort(409)
            connection.execute("INSERT INTO likes(owner, postid) VALUES "
                               "(?, ?)", (username, postid,))

        if operation == "unlike":
            # delete a like for postid
            # check if an unlike is already existed

            if check_like is None:
                flask.abort(409)
            connection.execute("DELETE FROM likes WHERE postid = ? AND "
                               "owner = ?", (postid, username,))

        target = flask.request.args.get("target")
        if target is None:
            target = "/"

        return flask.redirect(target)
    return flask.redirect(flask.url_for("login"))


# Deal with POST comment
@insta485.app.route("/comments/", methods=["POST"])
def comments():
    """Deal with POST likes."""
    if flask.request.method != "POST":
        return None

    if "logname" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    operation = flask.request.form["operation"]

    connection = insta485.model.get_db()
    username = flask.session["logname"]

    # create a new comment
    if operation == "create":
        text = flask.request.form["text"]
        postid = flask.request.form["postid"]
        if text == "":
            flask.abort(400)
        connection.execute("INSERT INTO comments(owner, postid, text) VALUES "
                           "(?, ?, ?)", (username, postid, text,))
    # delete a comment
    if operation == "delete":
        commentid = flask.request.form["commentid"]
        cur = connection.execute("SELECT * FROM comments WHERE commentid = ? "
                                 "AND owner = ? ", (commentid, username,))
        if cur.fetchone() is None:
            flask.abort(403)
        connection.execute("DELETE FROM comments WHERE commentid = ?",
                           (commentid,))

    target = flask.request.args.get("target")
    if target is None:
        target = "/"

    return flask.redirect(target)


@insta485.app.route("/accounts/logout/", methods=["POST"])
def logout():
    """Logout."""
    if flask.request.method != "POST":
        return None
    flask.session.clear()
    return flask.redirect("/accounts/login/")


# currently not useful
@insta485.app.route("/uploads/<string:filename>")
def get_pic(filename):
    """Get insta icon logo."""
    return flask.send_from_directory(insta485.app.config["UPLOAD_FOLDER"],
                                     filename, as_attachment=True)
