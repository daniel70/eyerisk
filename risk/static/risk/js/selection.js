// this file is no longer used

var SelectionBox = React.createClass({
    loadSelectionsFromServer: function() {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.setState({data: data});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    getInitialState: function() {
        return {data: []};
    },
    componentDidMount: function() {
        this.loadSelectionsFromServer();
    },
    render: function() {
        return (
            <div className="selectionBox">
                <h1>Selections</h1>
                <SelectionList data={this.state.data} />
            </div>
        );
    }
});

var SelectionList = React.createClass({
    render: function() {
        var selectionNodes = this.props.data.map(function(standard) {
            return (
                <Standard id={standard.id} key={standard.id}>
                    {standard.name}
                </Standard>
            );
        });
        return (
            <div className="selectionList">
                {selectionNodes}
            </div>
        );
    }
});

var Standard = React.createClass({
    render: function() {
        return (
            <div className="standard" id={this.props.id}>
                {this.props.children}
            </div>
        );
    }
});

ReactDOM.render(
  <SelectionBox url="/api/standards" />,
  document.getElementById('content')
);