import React from 'react';
import PropTypes from 'prop-types';

function CommentDeleteButton(props) {
  const {
    lognameOwnsThis, commentid, deleteComment, deleteUrl,
  } = props;
  if (lognameOwnsThis) {
    return (
      <button className="delete-comment-button" onClick={(e) => deleteComment(e, commentid, deleteUrl)} type="button">
        Delete Comment
      </button>
    );
  }
  return null;
}

function Comments(props) {
  const {
    ownerShowUrl, owner, text, commentid, lognameOwnsThis, deleteComment, deleteUrl,
  } = props;
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
          lognameOwnsThis={lognameOwnsThis}
          commentid={commentid}
          deleteComment={deleteComment}
          deleteUrl={deleteUrl}
        />
      </p>
    </div>
  );
}

CommentDeleteButton.propTypes = {
  lognameOwnsThis: PropTypes.bool.isRequired,
  commentid: PropTypes.number.isRequired,
  deleteComment: PropTypes.func.isRequired,
  deleteUrl: PropTypes.string.isRequired,
};

Comments.propTypes = {
  text: PropTypes.string.isRequired,
  ownerShowUrl: PropTypes.string.isRequired,
  owner: PropTypes.string.isRequired,
  commentid: PropTypes.number.isRequired,
  lognameOwnsThis: PropTypes.bool.isRequired,
  deleteComment: PropTypes.func.isRequired,
  deleteUrl: PropTypes.string.isRequired,
};

export default Comments;
