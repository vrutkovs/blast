class SearchResults extends React.Component {
  render() {
    if (this.props.results.length == 0) {
      return (
        <p>Sorry, no results.</p>
      );
    } else {
      return(
        <div>
          {this.props.results.map(item => (
            <p>
              <span>{item.title}</span>
              <img src={item.url} alt={item.title}></img>
            </p>
          ))}
        </div>
      );
    }
  }
}

class SearchBar extends React.Component {
  constructor(props) {
    super(props);

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleInputChange(event) {
    this.props.onSearchInput(event.target.value);
  }

  handleSubmit(event) {
    this.props.onSearchSubmit(event);
  }

  render() {
    return (
      <ReactBootstrap.Form horizontal>
        <ReactBootstrap.FormGroup>
          <ReactBootstrap.Col sm={11}>
            <ReactBootstrap.FormControl
              autoFocus="true"
              type="text"
              placeholder="Search..."
              value={this.props.searchInput}
              onChange={this.handleInputChange}
            />
          </ReactBootstrap.Col>
          <ReactBootstrap.Col sm={1}>
            <ReactBootstrap.Button
              type="submit"
              onClick={this.handleSubmit}>
              Search
            </ReactBootstrap.Button>
          </ReactBootstrap.Col>
        </ReactBootstrap.FormGroup>
      </ReactBootstrap.Form>
    );
  }
}


class SearchForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      searchInput: '',
      results: [],
    };

    this.handleSearchInput = this.handleSearchInput.bind(this);
    this.handleSearchSubmit = this.handleSearchSubmit.bind(this);
  }

  handleSearchInput(searchInput) {
    this.setState({searchInput: searchInput});
  }

  handleSearchSubmit(event) {
    event.preventDefault();
    if (this.state.searchInput.length == 0) {
      return;
    }

    // this piece of code assumes certain naming conventions
    // of the backend services
    var hostname = window.location.hostname
    var postfix = hostname.substring(hostname.indexOf("-"));

    fetch('http://api' + postfix + "/api/v1.0/search/" + this.state.searchInput)
      .then(result=>result.json())
      .then(items=>this.setState({results: items}));
  }

  render() {
    return (
      <div>
        <h3>CatCatGo</h3>
        <SearchBar
          searchInput={this.state.searchInput}
          onSearchInput={this.handleSearchInput}
          onSearchSubmit={this.handleSearchSubmit}
        />
        <br />
        <SearchResults results={this.state.results} />
      </div>
    );
  }
}

ReactDOM.render(
  <SearchForm />,
  document.getElementById('container')
);
