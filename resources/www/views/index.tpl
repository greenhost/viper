<html>
<header>
	<title>{{title}}</title>
	<script type="text/javascript" src="/resources/jquery-1.11.1.min.js"></script>
	<style>
		#col2 {
			width: 220px;
			float: left;
			margin: 80px 0 0 60px;
		}
		
		p {
			padding: 0;
			margin: 0;
		}

		img {
			margin: 40px 0 0 0;
		}

		h2 {
			color: #333333;
			font-family: Impact, Charcoal, sans-serif;
			letter-spacing: 35px;
			margin: 0;
			padding: 0;
			line-height: 1em;
		}

		small {
			font-size: 0.65em;
			margin: 0.25em 0 0 0;
			color: #333333;
			font-family: courier,	/* Unix+X, MacOS */ monospace;
		}

		button {
			margin: 12px 0 12px 0;
			padding: 8px 12px 8px 12px;
			display: block;
			width: 100%;
		}

		select {
			padding: 8px 12px 8px 12px;
			width: 100%;
		}

		#notification {
			margin: 1em 0 1em 0;
			padding: 12px 0 12px 0;
			text-align: center;
		}

		.yellow {
			background: #ffff80;
		}
	</style>
</header>
<body>
	<noscript>Your broser doesn't support Javascript</noscript>
	<div id="container">
		<div id="notification" class="yellow">TUNNEL STATUS</div>
		<div id="policies" class="yellow">policies</div>
		<button id="btnCheckStatus">Check status</button>
		<!-- 
		<button id="btnOpenTunnel">Open secure tunnel</button>
		<button id="btnCloseTunnel">Close secure tunnel</button>
		<select id="slctPolicy" name="policy">
		-->
		</select>
	</div>

<script>
$(document).ready(function () {
	//$('#notification').hide();

	function displayStatus() {
		$.getJSON("/tunnel/status", function(data) {
			if(data['state'].toUpperCase() == "CONNECTED") {
				$("#notification").css("background", "#aaffaa");
			    $("#notification").html(data['state']);
			} else {
				$("#notification").css("background", "#ffaaaa");
			    $("#notification").html(data['state']);
			}
		});
/*
		$.ajax({url: "/policy",
			    contentType : 'application/json',
			    type : 'OPTIONS',
				success: function(data) {
	    				var html = "<p>with policies: "+data;

						// $.each(data, function(index, value){
						// 	html += "<li>"+value+"</li>";
					 //    });

						html += "</p>";
					    $("#policies").html( html ); //JSON.stringify(data) );
				      },
      	    });
*/
	}

	displayStatus();

	/* get list of available policies */
/*
	$.getJSON("/policy", function(data) {
	    $.each(data, function(index, value){
	    	//console.log(value);
	        $("#slctPolicy").append('<option value="'+ value +'">'+ value +'</option>');
	    });
	});

	$('#btnCheckStatus').click(function () {
		displayStatus();
	});

	$('#btnOpenTunnel').click(function () {
		$.ajax({url: "/tunnel/open",
			    data : JSON.stringify( {config: "config.ovpn", log: "greenhost.log" } ),
			    contentType : 'application/json',
			    type : 'POST'
	    });
	    displayStatus();
	});

	$('#btnCloseTunnel').click(function () {
		$.ajax({url: "/tunnel/close",
			    contentType : 'application/json',
			    type : 'POST'
	    });
		displayStatus();
	});

	$("#slctPolicy").change(function() {
		$.ajax({url: "/policy/enable",
			    contentType : 'application/json',
			    type : 'POST',
			    data: JSON.stringify( {name: $(this).val()} )
	    });
	    displayStatus();
	});
*/

});
</script>

</body>
</html>
<!--
/tunnel/open
    curl -X POST -i -H "Content-type: application/json" http://localhost:8080/tunnel/open -d '{"config":"/etc/greenhost.ovpn","log":"greenhost-ovpn.log"}'
/tunnel/close
    curl -X POST -i -H "Content-type: application/json" http://localhost:8080/tunnel/close
/tunnel/status
    curl -X GET -i http://localhost:8080/tunnel/status
/policy
    curl -X GET -i http://localhost:8080/policy
/policy
    curl -X OPTIONS -i http://localhost:8080/policy
/policy/enable
    curl -X POST -i -H "Content-type: application/json" http://localhost:8080/policy/enable -d '"name"="ipv6"'
/policy/setting
    curl -X POST -i -H "Content-type: application/json" http://localhost:8080/policy/setting -d '{"name"="ipv6", "settings" : {"timeout" : 100}}'
/policy/disable
    curl -X POST -i -H "Content-type: application/json" http://localhost:8080/policy/disable -d '"name"="ipv6"'
-->