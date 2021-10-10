import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import Comments from './comments';

class IndividualPost extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      comments: [],
      created: '',
      imgUrl: '',
      likes: {},
      owner: '',
      ownerImgUrl: '',
      ownerShowUrl: '',
      postShowUrl: '',
      postid: null,
      newcomment: '',
    };
    this.deleteComment = this.deleteComment.bind(this);
    this.commentSubmit = this.commentSubmit.bind(this);
    this.unlikePost = this.unlikePost.bind(this);
    this.likePost = this.likePost.bind(this);
  }

  componentDidMount() {
    const { url } = this.props;
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          comments: data.comments,
          created: data.created,
          imgUrl: data.imgUrl,
          likes: data.likes,
          owner: data.owner,
          ownerImgUrl: data.ownerImgUrl,
          ownerShowUrl: data.ownerShowUrl,
          postid: data.postid,
        });
      })
      .catch((error) => console.log(error));
  }

  commentSubmit(e) {
    if (e.target.value !== '') {
      e.preventDefault();
      const addCommentUrl = '/api/v1/comments/';
      const { postid } = this.state;
      const { newcomment } = this.state;
      const combine = `${addCommentUrl}?postid=${postid}`;
      fetch(combine, { method: 'POST', credentials: 'same-origin', body: JSON.stringify({ text: newcomment }) })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState((prevState) => ({
            comments: prevState.comments.concat(data),
          }));
        })
        .then(() => {
          this.setState({ newcomment: '' });
        })
        .catch((error) => console.log(error));
    }
  }

  // delete a comment
  deleteComment(e, commentid, deleteUrl) {
    e.preventDefault();
    this.setState((prevState) => ({
      comments: prevState.comments.filter((sub) => sub.commentid !== commentid),
    }));
    fetch(deleteUrl, { method: 'DELETE', credentials: 'same-origin' });
  }

  // unlike a post
  unlikePost(e, oneLikeUrl) {
    e.preventDefault();
    const { likes } = this.state;
    const update = { lognameLikesThis: false, numLikes: likes.numLikes - 1, url: null };
    this.setState({ likes: update });
    fetch(oneLikeUrl, { method: 'DELETE', credentials: 'same-origin' });
  }

  // like a post
  likePost(e) {
    e.preventDefault();
    const likesUrl = '/api/v1/likes/';
    const { postid } = this.state;
    const combine = `${likesUrl}?postid=${postid}`;
    const { likes } = this.state;
    fetch(combine, { method: 'POST', credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const update = { lognameLikesThis: true, numLikes: likes.numLikes + 1, url: data.url };
        this.setState({ likes: update });
      })
      .catch((error) => console.log(error));
  }

  render() {
    const {
      comments, created, likes, imgUrl, owner, ownerImgUrl,
      ownerShowUrl, postShowUrl, newcomment,
    } = this.state;

    const subComment = [];
    comments.forEach((sub) => {
      subComment.push(
        <Comments
          owner={sub.owner}
          ownerShowUrl={sub.ownerShowUrl}
          lognameOwnsThis={sub.lognameOwnsThis}
          text={sub.text}
          commentid={sub.commentid}
          deleteComment={this.deleteComment}
          deleteUrl={sub.url}
          key={sub.commentid}
        />,
      );
    });

    // let timer;

    function clickEvent(event, lognameLikesThis, url, unlikePost, likePost) {
      event.preventDefault();
      // clearTimeout(timer);
      // if (event.detail === 1) {
      //   timer = setTimeout(onClick, 200);
      // } else if (event.detail === 2) {
      //   if (lognameLikesThis) {
      //     this.unlikePost(url);
      //   } else {
      //     this.likePost();
      //   }
      // }
      if (lognameLikesThis) {
        unlikePost(event, url);
      } else {
        likePost(event);
      }
    }
    // onClick={(e) => clickEvent(e, likes.lognameLikesThis, likes.url, onClick)}
    return (
      <div className="middlePart">
        <a className="hyperlinkstyle" href={ownerShowUrl}>
          <img src={ownerImgUrl} alt="description for user" width="40" style={{ position: 'absolute' }} />
          <div style={{ position: 'absolute', top: '15px', left: '50px' }}>
            <b>{owner}</b>
          </div>
        </a>
        <a className="hyperlinkstyle" href={postShowUrl}>
          <div className="created">
            {moment(created).fromNow()}
          </div>
        </a>
        <br />
        <br />
        <br />
        <img className="post1" src={imgUrl} alt="desciption of post" onDoubleClick={(e) => clickEvent(e, likes.lognameLikesThis, likes.url, this.unlikePost, this.likePost)} />
        <br />
        <ShowLikeButton
          lognameLikesThis={likes.lognameLikesThis}
          unlikePost={this.unlikePost}
          likePost={this.likePost}
          oneLikeUrl={likes.url}
        />
        <br />
        <Like numLikes={likes.numLikes} />
        <ul>{subComment}</ul>
        <form className="comment-form" onSubmit={this.commentSubmit} style={{ marginLeft: '2rem', marginBottom: '1rem' }}>
          <input type="text" name="comment_text" value={newcomment} onChange={(e) => this.setState({ newcomment: e.target.value })} />
          <noscript>
            <input type="submit" name="comment_submit" value="Submit" />
          </noscript>
        </form>
      </div>
    );
  }
}

function Like(props) {
  const { numLikes } = props;
  let likegrammar;
  if (numLikes !== 1) {
    likegrammar = 'likes';
  } else {
    likegrammar = 'like';
  }
  return (
    <p style={{ marginLeft: '1.5rem' }}>
      {numLikes}
      <span style={{ marginLeft: '.5rem' }}>
        {likegrammar}
      </span>
      <br />
    </p>
  );
}

function ShowLikeButton(props) {
  const {
    lognameLikesThis, unlikePost, likePost, oneLikeUrl,
  } = props;
  if (lognameLikesThis) {
    return (
      <button className="like-unlike-button" onClick={(e) => unlikePost(e, oneLikeUrl)} type="button" style={{ marginLeft: '1.5rem' }}>
        Unlike
      </button>
    );
  }
  return (
    <button className="like-unlike-button" onClick={(e) => likePost(e)} type="button" style={{ marginLeft: '1.5rem' }}>
      Like
    </button>
  );
}

Like.propTypes = {
  numLikes: PropTypes.number.isRequired,
};

ShowLikeButton.propTypes = {
  lognameLikesThis: PropTypes.bool.isRequired,
  unlikePost: PropTypes.func.isRequired,
  likePost: PropTypes.func.isRequired,
  oneLikeUrl: PropTypes.string,
};

ShowLikeButton.defaultProps = {
  oneLikeUrl: null,
};

IndividualPost.propTypes = {
  url: PropTypes.string.isRequired,
};

export default IndividualPost;
