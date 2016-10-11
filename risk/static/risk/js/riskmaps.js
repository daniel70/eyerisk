var RiskMapBox = React.createClass({
    loadRiskMaps: function() {
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
        this.loadRiskMaps();
    },
    render: function () {
        return (
            <div className="riskmapBox">
                <RiskMapList data={this.state.data} />
            </div>
        );
    }
});

var RiskMapList = React.createClass({
    render: function() {
        var riskmapNodes = this.props.data.map(function(riskmap) {
            return (
                <div><textarea cols="70" rows="7">{riskmap.definition}</textarea></div>
            );
        });
        return (
            <div className="riskmapList">
                {riskmapNodes}
            </div>
        );
    }
});

ReactDOM.render(
    <RiskMapBox url='/api/riskmaps' />,
    document.getElementById('content')
);