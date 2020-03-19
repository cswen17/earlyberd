'use strict';

const e = React.createElement;

class QuoteJumbotron extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            quote: "It seems there is no Bible Quote available",
            comment: "Enter through the Narrow Gate",
            url: "",
            quoter: "Narrow Gate",
            loaded: false
        };
    }

    componentDidMount() {
        fetch("/quote")
          .then(response => {
              return response.json();
          })
          .then(data => {
              this.setState(() => {
                  return {
                      loaded: true,
                      quote: data[0]["fields"]["quote"],
                      comment: data[0]["fields"]["comment"],
                      quoter: data[0]["fields"]["quoter"],
                      url: data[0]["fields"]["image"]
                  };
              });
          });
    }

    render() {
        return React.createElement("div", {
    class: "jumbotron jumbotron-fluid my-5 p-0 d-flex shadow-lg"
  }, React.createElement("div", {
    class: "px-5 w-50 align-self-center"
  }, React.createElement("h2", {
    class: "font-weight-bold"
  }, this.state.comment), React.createElement("p", {
    class: "lead my-3"
  }, this.state.quote), React.createElement("button", {
    class: "rounded-sm btn btn-dark btn-lg text-decoration-none"
  }, this.state.quoter)), React.createElement("div", {
    class: "ml-auto mr-5 flex-fill"
  }, React.createElement("img", {
    src: this.state.url,
    height: "349px",
    width: "680px"
  })));
    }
}

const domContainer = document.querySelector('#quote_container');
ReactDOM.render(e(QuoteJumbotron), domContainer);
