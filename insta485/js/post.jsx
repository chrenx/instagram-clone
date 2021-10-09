import React from 'react';
import PropTypes from 'prop-types';
import IndividualPost from './individualPost';

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
        <IndividualPost url={sub.url} key={sub.postid} />,
      );
    });
    return (
      <div className="post">
        {subResult}
      </div>
    );
  }
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Posts;
