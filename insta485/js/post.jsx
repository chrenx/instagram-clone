import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import IndividualPost from './individualPost';

class Posts extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      results: [],
      next: '',
      allLength: 0,
      hasMore: true,
    };
    this.refresh = this.refresh.bind(this);
  }

  componentDidMount() {
    const { url } = this.props;

    window.onpopstate = () => {
      window.history.back();
    }

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
      })
      .catch((error) => console.log(error));
    const { results } = this.state;
    this.setState((prevState) => ({
      allLength: prevState.allLength + results.length,
    }));
    const { next } = this.state;
    if (next === '') {
      this.setState({ hasMore: false });
    }
    // const { allposts } = this.state;
    // const { results } = this.state;
    // results.forEach((sub) => {
    //   allposts.push(
    //     <IndividualPost url={sub.url} key={sub.postid} />,
    //   );
    // });
  }

  refresh() {
    const { next } = this.state;
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
        })
        .catch((error) => console.log(error));
    } else {
      this.setState({ hasMore: false });
    }
  }

  render() {
    // const subResult = [];
    // const { results } = this.state;
    // results.forEach((sub) => {
    //   allposts.push(
    //     <IndividualPost url={sub.url} key={sub.postid} />,
    //   );
    // });
    // Object.keys(results).length
    const { allLength } = this.state;
    const { results } = this.state;
    const { hasMore } = this.state;

    return (
      <div className="post">
        <InfiniteScroll
          dataLength={allLength}
          next={this.refresh}
          hasMore={hasMore}
          loader={<h4>Loading...</h4>}
          endMessage={(
            <p style={{ textAlign: 'center', marginTop: '9rem' }}>
              <b>Yay! You have seen it all</b>
            </p>
          )}
        >
          {results.map((sub) => (
            <IndividualPost url={sub.url} key={sub.postid} />
          ))}
        </InfiniteScroll>
      </div>
    );
  }
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Posts;
