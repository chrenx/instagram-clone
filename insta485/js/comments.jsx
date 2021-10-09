import React from 'react';
import PropTypes from 'prop-types';

class CommentDeleteButton extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      text: '',
      owner: '',
    };
  }

  deleteCommentFunc(e) {
    e.preventDefault();
    const { url } = this.props;
    fetch(url, { method: 'DELETE' })
      .then(() => {
        this.setState({text: ''});
        this.setState({owner: ''});
      });
    return null;
    // .then((response) => {
    //   if (!response.ok) throw Error(response.statusText);
    //   return response.json(); 
    // });
  }

  render() {
    const {
      lognameOwnsThis,
    } = this.props;
    if (lognameOwnsThis) {
      return (
        <button className="delete-comment-button" onClick={this.deleteCommentFunc.bind(this)} type="button">
          Delete Comment
        </button>
      );
    }
    return null;
  }
}

function Comments(props) {
  const {
    ownerShowUrl, owner, text, commentid, lognameOwnsThis, url,
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
          text={text}
          owner={owner}
          lognameOwnsThis={lognameOwnsThis}
          url={url}
          key={commentid}
        />
      </p>
    </div>
  );
}

CommentDeleteButton.propTypes = {
  text: PropTypes.string.isRequired,
  owner: PropTypes.string.isRequired,
  lognameOwnsThis: PropTypes.bool.isRequired,
  url: PropTypes.string.isRequired,
};

Comments.propTypes = {
  text: PropTypes.string.isRequired,
  ownerShowUrl: PropTypes.string.isRequired,
  owner: PropTypes.string.isRequired,
  commentid: PropTypes.number.isRequired,
  lognameOwnsThis: PropTypes.bool.isRequired,
  url: PropTypes.string.isRequired,
};

export default Comments;
