/**
 * @jsx React.DOM
 */

var AccountInfo = React.createClass({
	getInitialState: function() {
		return {
			username:null, 
			password:null
		};
	},
	logout: function() {
		this.props.onLogout();
	},
	render: function() {
		return  (
			<div className="row">
				<span>Welcome, {this.props.username}</span>
				<button 
					className="btn btn-primary ladda-button" 
					data-style="expand-right"
					data-size="s"
					onClick={this.logout}>

					Logout

				</button>
			</div>
		)
	}
});