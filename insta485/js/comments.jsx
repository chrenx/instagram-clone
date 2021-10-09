import React from 'react';
import PropTypes from 'prop-types';

function deleteCommentFunc(props) {

}

function CommentDeleteButton(props) {
    const {
      commentid,
      lognameOwnsThis,
      url
    } = props;
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

class Comments extends React.Component {
  render() {
    const { ownerShowUrl, owner, text, commentid, lognameOwnsThis, url } = this.props;
    return (
      <div>
        <p>
          <a className="hyperlinkstyle" href={ownerShowUrl}>
            <b style={{ marginRight: '.5rem' }}>{owner}</b>
          </a>
          <span style={{ marginRight: '.5rem' }}>
            {text}
          </span>
          <CommentDeleteButton
            commentid={commentid}
            lognameOwnsThis={lognameOwnsThis}
            url={url}
            key={commentid}
          />
        </p>
      </div>
    );
  }
}

Comments.propTypes = {
  text: PropTypes.string.isRequired,
  ownerShowUrl: PropTypes.string.isRequired,
  owner: PropTypes.string.isRequired,
  commentid: PropTypes.number.isRequired,
  lognameOwnsThis: PropTypes.bool.isRequired,
  url: PropTypes.string.isRequired,
};

export default Comments;
