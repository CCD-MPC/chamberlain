

<template>
    
	<div id="about">
		<a href="https://github.com/multiparty/conclave" target="_blank">
				Conclave Github
		</a>
		<div class = 'section-banner' id="section-1">
			<div id = 'tint-overlay'>
				
			</div>
			<div id="section-1-textOverlay">
				<div id = 'h1-overlay'>
					<h1>CICI Data Processing</h1>
				</div>
				<div id="h2-overlay">
					<h2>Where you process data</h2>
				</div>
			</div>
		</div>
		<div class = 'section-banner' id="section-2">
			<div id = 'contacts'>
				<div id="contacts-wrapper">
					<ContactTemplate author = 'Graeme M.' title = 'Genius Programmer' profileURL = 'http://www.stickpng.com/assets/images/584830bfcef1014c0b5e4a9d.png' />
					<ContactTemplate author = 'Jacob D.' title = 'Less-Genius Programmer' profileURL = 'http://www.stickpng.com/assets/images/584830bfcef1014c0b5e4a9d.png' />
					<ContactTemplate author = 'G-Money' title = 'Company Rapper' profileURL = 'http://www.stickpng.com/assets/images/584830bfcef1014c0b5e4a9d.png' />
					<ContactTemplate author = 'Graeme' title = 'Genius Programmer' profileURL = 'http://www.stickpng.com/assets/images/584830bfcef1014c0b5e4a9d.png' />
				</div>
			</div>
			<div id='team-description'>
				<div id="team-description-header">
					<h2>Meet the Team</h2>
				</div>
				<div id="team-description-text">
					<p>The CICI team has been working with the utmost efficiency and teamwork, pulling together the abilities of each member to create a functioning product to be proud of</p>
				</div>
			</div>
		</div>
		<div class = 'section-banner' id="footer">

		</div>
	</div>
</template>

<script>
import ContactTemplate from './ContactTemplate.vue';

export default {
	components: {
		ContactTemplate
	}
}
</script>


<!-- styling for the component -->
<style lang='css'>
	@import '../../node_modules/bulma/css/bulma.css';
	#about {
			font-family: 'overpass-bold';
			-webkit-font-smoothing: antialiased;
			-moz-osx-font-smoothing: grayscale;
			text-align: center;
			color: #2c3e50;
			margin-top: 10px;

	}
	.section-banner {
		width: 100%;
		position:relative;
		margin: 0 auto;

		font-family: 'overpass-light';
		color: #fafafa;
	}

/* ======Section 1=========*/
	#section-1 {
		text-align:left;
		height: 40vh; 

		background-image: url('https://structuretone.com/wp-content/uploads/2014/02/IA_Red-Hat_Boston_Robert-Benson-26_web.jpg');
		background-size: cover;
	}
	#tint-overlay {
		width: 100%;
		height: 100%;
		background: #030303;
		opacity: .5;
	}

	#h1-overlay {
		position: absolute;	
		
		font-size: 50px;
		top: 20px;
		left:20px;
	}
	#h2-overlay{
		position: absolute;
		font-size: 30px;
		top: 100px;
		left: 20px;
	}
/* =========Section 2============= */

	#section-2{
		height: 40vh;
		background: linear-gradient(#fafafa, #ededed);

		display: flex;
		
		
	}

	#contacts-wrapper{
		padding-left: 10%;
		padding-top: 10px;	
		width: 250px !important;
		display: flex;
		flex-direction: column;
		
	}
	
	#team-description{
		
		color: #0088ce;
		display:flex;
		flex-direction: column;
		padding-right: 20px;
	}
	#team-description-header{
		font-size: 40px;
		text-align: right;
	}
	#team-description-text{
		font-size: 20px;
		text-align: right;
	}


	/* helper classes */
	.darken {
		content: "";
		display: block;
		position: absolute;

		left: 0;
		right: 0;
		background:#030303;
		
	}
    
</style>
