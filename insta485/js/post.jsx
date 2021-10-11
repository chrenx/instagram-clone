import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import IndividualPost from './individualPost';

class Posts extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      allposts: [],
      results: [],
      next: '',
      allLength: 0,
      hasMore: true,
      // lognameLikesThis: true,
      // numLikes: null,
      // likesUrl: null,
    };
    this.refresh = this.refresh.bind(this);
  }

  componentDidMount() {
    performance.mark('Begin');
    window.onpopstate = () => {
      window.history.back();
    };
    performance.mark('End');
    setTimeout(() => {
      const { url } = this.props;
      // const { allposts } = this.state;
      this.setState({
        next: url,
      });
      this.setState({ hasMore: true });
      fetch(url, { credentials: 'same-origin' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState({
            results: data.results,
            next: data.next,
          });

          const { results } = this.state;
          const { allposts } = this.state;
          results.forEach((sub) => {
            allposts.push(
              <IndividualPost
                url={sub.url}
                lognameLikesThis={sub.likes.lognameLikesThis}
                numLikes={sub.likes.numLikes}
                likesUrl={sub.likes.url}
                key={sub.postid}
              />,
            );
          });

          this.setState((prevState) => ({
            allLength: prevState.allLength + results.length,
          }));

          this.setState({ hasMore: true });
        })
        .catch((error) => console.log(error));
    }, 500);
  }

  refresh() {
    performance.mark('Begin');
    window.onpopstate = () => {
      window.history.back();
    };
    performance.mark('End');
    const { next } = this.state;
    const { allposts } = this.state;
    if (next !== '') {
      // process next url
      fetch(next, { credentials: 'same-origin' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          this.setState({
            results: data.results,
            next: data.next,
          });

          const { results } = this.state;

          results.forEach((sub) => {
            allposts.push(
              <IndividualPost
                url={sub.url}
                lognameLikesThis={sub.likes.lognameLikesThis}
                numLikes={sub.likes.numLikes}
                likesUrl={sub.likes.url}
                key={sub.postid}
              />,
            );
          });

          this.setState((prevState) => ({
            allLength: prevState.allLength + results.length,
          }));

          this.setState({ hasMore: true });
        })
        .catch((error) => console.log(error));
    } else {
      this.setState({ hasMore: false });
    }
  }

  render() {
    const { allLength } = this.state;
    const { allposts } = this.state;
    const { hasMore } = this.state;

    return (
      <InfiniteScroll
        dataLength={allLength}
        next={this.refresh}
        hasMore={hasMore}
        loader={<h4>加载...</h4>}
        endMessage={(
          <p style={{ textAlign: 'center', marginTop: '9rem' }}>
            <b>Yay! You have seen it all</b>
          </p>
        )}
      >
        <div className="post">
          {allposts}
        </div>
      </InfiniteScroll>
    );
  }
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Posts;
