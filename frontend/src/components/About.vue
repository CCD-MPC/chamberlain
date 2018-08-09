<template>
	<div id="about">
		<div class = 'section-banner' id="section-1">
			<div id = 'tint-overlay'>
				
			</div>
			<div id="section-1-textOverlay">
				<div class = 'topHeader' id = 'h1-overlay'>
					<h1>CICI Data Processing</h1>
				</div>
				<div class = 'topSubtext' id="h2-overlay">
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
					<ContactTemplate author = 'Ben G.' title = 'Genius Programmer' profileURL = 'http://www.stickpng.com/assets/images/584830bfcef1014c0b5e4a9d.png' />
				</div>
			</div>
			<div id='team-description'>
				<div id="team-description-header">
					<h2 class = 'header'>Meet the Team</h2>
				</div>
				<div class = 'subtext' id="team-description-text">
					<p>The CICI team has been working with the utmost efficiency and teamwork, pulling together the abilities of each member to create a functioning product to be proud of</p>
				</div>
			</div>
		</div>
		<div class="section-banner" id = "github">
			<div id = 'github-description'>
				<div id="github-header">
					<h2 class = 'header'>Learn More</h2>
				</div>
				<div class = 'subtext' id="github-text">
					<p>Check out our github to take a closer look at CICI</p>
				</div>
			</div>
			<div id="github-link">
				<a href="https://github.com/multiparty/conclave" target="_blank">
					<img href="https://github.com/multiparty/conclave" src='../../assets/GitHub-Mark-120px-plus.png' style = 'width: 80px; height: 80px;'>
				</a>
			</div>
		</div>
		<div class = 'section-banner' id="footer">
			<div id="footer-container">
				<div class='footer-section'>
					<h2 class='footer-header'>About</h2>
					<a href="" class='footer-link'>Methodology</a>
					<a href="" class='footer-link'>Soundcloud</a>
					<a href="" class='footer-link'>Spotify playlist</a>
					<a href="" class="footer-link">Philosophy 101</a>
				</div>
				<div class='footer-section'>
					<h2 class='footer-header'>Support</h2>
					<a href="" class="footer-link">One Fish</a>
					<a href="" class="footer-link">Two Fish</a>
					<a href="" class="footer-link">Red Fish</a>
					<a href="" class="footer-link">Blue Fish</a>
				</div>
				<div class='footer-section'>
					<h2 class = 'footer-header'>Contact</h2>
					<a href="" class="footer-link">Ben G.</a>
					<a href="" class="footer-link">Jacob D.</a>
					<a href="" class="footer-link">Graeme M.</a>
					<a href="" class="footer-link">G-Money</a>
				</div>
				<div class='footer-section'>
					<h2 class='footer-header'>Other</h2>
					<a href="" class="footer-link">Link One</a>
					<a href="" class="footer-link">Link Two</a>
					<a href="" class="footer-link">Link Three</a>
				</div>
			</div>
			<p id="footer-info">
				Red Hat 2018 © Copyright
			</p>
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
		top: 10px;
		left: 10px;
	}
	#h2-overlay{
		position:absolute;
		top: 130px;
		left: 10px;
	}
/* =========Section 2============= */

	#section-2{
		flex-direction: column;
		background: linear-gradient(#fafafa, #ededed);
		padding-bottom: 20px;
		display: flex;
	}

	#contacts-wrapper{
		padding-left: 10%;
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
		text-align: right;
	}
	#team-description-text{
		text-align: right;
	}

/* =========Section 3 / github Link ======*/

	#github{
		background-image: url('../../assets/blueBackground.png');
		background-size: cover;
		display: flex;
		flex-direction:column;

		padding-top: 20px;
		padding-bottom: 20px;
	}
	#github-description{
		display: flex;
		flex-direction: column;
		text-align: left;
		margin-bottom: 50px;
	}
	#github-header {
		margin-bottom: 15px;
	}
/* ============ Footer ============*/
	#footer{
		background-color: #030303;
	}
	#footer-container{
		width: 100%;
		display:flex;
	}

	.footer-section {
		display:flex;
		flex-direction: column;

		margin-top: 5px;
		margin-bottom: 5px;
		width: 25%;
	}
	.footer-header {
		color:#0088ce;
		font-size: 20px;
	}
	.footer-link{
		font-size: 12px;
		margin-top: 8px;
		text-align: center;
		color: white;
	}
	#footer-info{
		font-size: 12px;
		color:lightgrey;
	}

	.topHeader{
		font-size: 40px;
	}
	.topSubtext {
		font-size: 20px;
	}
	.header{
		font-size: 30px;
	}
	.subtext{
		font-size: 15px;
	}
	#github-link{
		margin: 0 auto;
	}

	/* helper classes */
	

	@media (min-width: 768px) {
		#section-2 {
			flex-direction: row;
		}
		#github {
			flex-direction: row;
		} 
		.topHeader{
			font-size: 50px;
		}
		.topSubtext{
			font-size: 30px;
		}
		.header{
			font-size: 40px;
		}
		.subtext {
			font-size: 20px;
		}
		.footer-section {
			margin-bottom: 15px;
		}
		.footer-header{
			margin-bottom: 15px;
		}
	}
	@media (min-width: 420px) {
		.topHeader {
			top: 20px;
			left: 20px;
		}
		.topSubtext {
			top: 100px;
			left: 20px;
		}

		.footer-link {
			font-size: 15px;
			margin-top: 5px;
		}
	}
</style>
