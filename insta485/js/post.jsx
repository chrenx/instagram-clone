import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';

function deleteCommentFunc(url, commentid) {

}

function CommentDeleteButton(props) {
  const { commentid, lognameOwnsThis, url } = props;
  if (lognameOwnsThis) {
    return (
      <button className="delete-comment-button" onClick={deleteCommentFunc(url, commentid)} >
        Delete Comment
      </button>
    );
  } else {
    return null;
  }
}

function Comments(props) {
  const { commentid, lognameOwnsThis, owner, ownerShowUrl, text, url } = props;
  return(
    <div>
      <p>
        <a className='hyperlinkstyle' href={ownerShowUrl} >
          <b style={{marginRight:'.5rem'}}>{owner}</b>
        </a>
        {text}
        <span style={{marginRight:'.5rem'}}></span>
        <CommentDeleteButton
          commentid={commentid}
          lognameOwnsThis={lognameOwnsThis}
          url={url}
        />
      </p>
    </div>
  );
}

function IndividualPost(props) {
  const subComment = [];
  const { comments, created, imgUrl, likes, owner, ownerImgUrl, ownerShowUrl, postShowUrl, postid, url } = props;
  comments.forEach((sub) => {
    subComment.push(
      <Comments
        commentid={sub.commentid}
        lognameOwnsThis={sub.lognameOwnsThis}
        owner={sub.owner}
        ownerShowUrl={sub.ownerShowUrl}
        text={sub.text}
        url={sub.url}
      />,
    );
  });

  return (
    // 放头像
    // 放用户名
    <div className='middlePart'>
      <a className='hyperlinkstyle' href={ownerShowUrl} >
        <img src={ownerImgUrl} alt='image for user' width='40' style={{position:'absolute'}} />
        <div style={{position:'absolute', top:'15px', left:'50px'}}>
          <b>{owner}</b>
        </div>
      </a>
      <a className='hyperlinkstyle' href={postShowUrl} >
        <div style={{} position: 'absolute', top: '15px', right: '0px', color: 'gray' }}>
          {moment(created).fromNow()}
        </div>
      </a>
      <br />
      <br />
      <br />
      <img className="post1" src={imgUrl} alt="desciption of post" />
      <br />
      <br />
      <ul>{subComment}</ul>
    </div>
    // 放照片
    // 放like button
    // 放几个like
    // 放所有comments
    // 放commets submit
  );
}

class Posts extends React.Component {
  constructor(props) {
    super(props);
    this.state = { results: [] };
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
          results: data.results,
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    const subResult = [];
    const { results } = this.state;
    results.forEach((sub) => {
      subResult.push(
        <IndividualPost
          comments={sub.comments}
          created={sub.created}
          imgUrl={sub.imgUrl}
          likes={sub.likes}
          owner={sub.owner}
          ownerImgUrl={sub.ownerImgUrl}
          ownerShowUrl={sub.ownerShowUrl}
          postShowUrl={sub.postShowUrl}
          postid={sub.postid}
          url={sub.url}
        />,
      );
    });
    return (
      <ul>{subResult}</ul>
    );
  }
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Posts;
