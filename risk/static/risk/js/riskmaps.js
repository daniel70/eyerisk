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
        // we use the following array to pick the properties and from the objects
        // and also the select unique entries based on the same array
        var pickunique = ['riskmap_id', 'level', 'name'];
        var nodes = _.uniqBy(_.map(this.state.data, _.partialRight(_.pick, pickunique)), pickunique);
        return (
            <div className="row">
                <div className="col-md-4">
                    <div className="riskmapBox">
                        <h1>Risk maps</h1>
                        <RiskMapList data={nodes} />
                    </div>
                </div>
                <div className="col-md-8">
                    <form action="" method="post">
                        <input type="submit" value="Update Risk Map" />
                    </form>
                </div>
            </div>
        );
    }
});

var RiskMapList = React.createClass({
    render: function() {
        var riskmapNodes = this.props.data.map(function(riskmap) {
            return (
                <div>{riskmap.level} - {riskmap.name}</div>
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