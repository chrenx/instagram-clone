import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';


class IndividualPost extends React.Component {
    constructor(props) {
        super(props);
        // this.state = { comments: props.comments, created: props.created,
        //                imgUrl: props.imgUrl, likes: props.likes,
        //                owner: props.owner, ownerImgUrl: , ownerShowUrl: '',
        //                postShowUrl: '', postid: null, url: '' };
    }

    componentDidMount() {
        // this.setState({
        //     comments: this.props.comments,
        //     created: this.props.created,
        //     imgUrl: this.props.imgUrl,
        //     likes: this.props.likes,
        //     owner: this.props.owner,
        //     ownerImgUrl: this.props.ownerImgUrl,
        //     ownerShowUrl: this.props.ownerShowUrl,
        //     postShowUrl: this.props.postShowUrl,
        //     postid: this.props.postid,
        //     url: this.props.url,
        // });
    }

    render() {
        
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
                <br /><br /><br />
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
                    key={sub.postid} />
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
