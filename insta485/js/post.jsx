import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';


function deleteCommentFunc(url, commentid) {

}


class CommentDeleteButton extends React.Component {
    constructor(props) {
        super(props)
    }

    componentDidMount() {

    }

    deleteCommentFunc(url, commentid) {
        return (
            <form action={url} method="DELETE" enctype="multipart/form-data">
                <input type="hidden" name="operation" value="delete" />
                <input type="hidden" name="commentid" value={commentid} />
                <input type="submit" name="uncomment" value="delete" />
            </form>
        );
    }

    render() {
        if (this.props.lognameOwnsThis) {
            return (
                <button className="delete-comment-button" onClick={deleteCommentFunc(this.props.url, this.props.commentid)} >
                    Delete Comment
                </button>
                
            );
        } else {
            return null;
        }
    }
}


class Comments extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {

    }

    render() {
        return(
            <div>
                <p>
                <a className='hyperlinkstyle' href={this.props.ownerShowUrl} >
                    <b style={{marginRight:'.5rem'}}>{this.props.owner}</b>
                </a>
                {this.props.text}
                <span style={{marginRight:'.5rem'}}></span>
                <CommentDeleteButton 
                    commentid={this.props.commentid}
                    lognameOwnsThis={this.props.lognameOwnsThis}
                    url={this.props.url}
                />
                </p>
            </div>
        );
    }
}


class IndividualPost extends React.Component {
    constructor(props) {
        super(props);

    }

    componentDidMount() {

    }

    render() {
        const sub_comment = [];
        this.props.comments.forEach((sub) => {
            sub_comment.push(
                <Comments 
                    commentid={sub.commentid}
                    lognameOwnsThis={sub.lognameOwnsThis}
                    owner={sub.owner}
                    ownerShowUrl={sub.ownerShowUrl}
                    text={sub.text}
                    url={sub.url}
                    key={sub.commentid}
                />
            );
        });

        return (
            // 放头像
            // 放用户名
            <div className='middlePart'>
                <a className='hyperlinkstyle' href={this.props.ownerShowUrl} >
                    <img src={this.props.ownerImgUrl} alt='image for user' width='40' style={{position:'absolute'}} />
                    <div style={{position:'absolute', top:'15px', left:'50px'}}>
                        <b>{this.props.owner}</b>
                    </div>
                </a>
                <a className='hyperlinkstyle' href={this.props.postShowUrl} >
                    <div style={{position:'absolute', top:'15px', right:'0px', color:'gray'}}>
                        {moment(this.props.created).fromNow()}
                    </div>
                </a>
                <br /><br /><br />
                <img className="post1" src={this.props.imgUrl} alt='post image' />
                <br /><br />
                <ul>{sub_comment}</ul>
            </div>

            // 放照片
            // 放like button
            // 放几个like
            // 放所有comments
            // 放commets submit
        );
    }
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
        const sub_result = [];
        this.state.results.forEach((sub) => {
            sub_result.push(
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
                    key={sub.postid}
                />
            );
        });
        return (
            <ul>{sub_result}</ul>
        );
    }
}


Posts.propTypes = {
    url: PropTypes.string.isRequired,
};


export default Posts;
