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
    };
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

  render() {
    const {
      comments, created, imgUrl, likes, owner, ownerImgUrl, ownerShowUrl, postShowUrl, postid,
    } = this.state;

    const subComment = [];
    comments.forEach((sub) => {
      subComment.push(
        <Comments
          commentid={sub.commentid}
          lognameOwnsThis={sub.lognameOwnsThis}
          owner={sub.owner}
          ownerShowUrl={sub.ownerShowUrl}
          text={sub.text}
          url={sub.url}
          key={sub.commentid}
        />,
      );
    });

    return (
      // 放头像
      // 放用户名
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
}

IndividualPost.propTypes = {
  url: PropTypes.string.isRequired,
};

export default IndividualPost;
