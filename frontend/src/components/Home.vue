<!DOCTYPE html>


<template>
  <div id="home">
	  <form id = 'form' @submit.prevent="handleSubmit">
		  <div id = 'formWrapper'>
				<div id="formHeader">
					<h1>Get Started</h1>
				</div>
				<div class = 'FormStep' id="dataInput">
					<div id = 'dataInput-top'>
						<div class = 'formTitle' id="dataInput-title">
							<h1>Step 1: Specify Your Input Datasets</h1>
						</div>
						<div id="dataInput-addSet">
							<button id = 'addInput' class="button" @click="addData">Add A Dataset</button>
						</div>
					</div>
					<div id="tableWrapper">
						<table class="table">
							<tr v-for="(row) in dataRows" v-bind:key="row.id">
								<td class = 'formInput' id = 'endpointFile'>
									<input class = 'fileInput' id = 'Endpoint' type="file" @change='onFileChange'>
									<label for="file">Endpoint</label>
								</td>
								<td class = 'formInput' id = 'containerFile'>
									<input class = 'fileInput' id = 'Container' type="file" @change='onFileChange'>
									<label for="file">Container</label>
								</td>
								<td class = 'formInput' id = 'datasetFile'>
									<input class = 'fileInput' id = 'Dataset' type="file" @change='onFileChange'>
									<label for="file">Dataset</label>
								</td>
								<td>
									<a @click="removeData(row.id)" style="cursor: pointer">Remove</a>
								</td>
							</tr>
						</table>
					</div>
				</div>
				<div class="FormStep">
					<div class="formTitle">
						<h1>Step 2: Submit!</h1>
					</div>
					<div id = 'submitButton'>
						<button style = 'margin-left: 10px' class="button btn-primary is-pulled-left" type="submit" @click="submitData">Compute</button>
					</div>

				</div>
				<div class = 'FormStep' style = 'border-bottom: none; padding-top: 20px'>
					<button class="button btn-primary is-pulled-right" @click="getStatusFromBackend">Check Status</button>
					<p>Job Status: {{ jobStatus }} </p>
				</div>
		  </div>
	  </form>
  </div>
</template>

<style lang='css'>
	@import '../../node_modules/bulma/css/bulma.css';

	html, body {
		background: #fafafa;
		overflow: hidden;
	}
	#formWrapper {
		/* Positioning */
		width: 100%;
		max-width: 768px;
		margin: 0 auto;

		/* format */
		border-radius: 2px;
		border: darkgray 2px;
		/*background-color: white;*/
		color: #030303;
		/*box-shadow: 0 0.1em 1em 0 #bbb;*/
	}
	#home {
		font-family: 'Avenir', Helvetica, Arial, sans-serif;
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
		text-align: left;
		margin-top: 0px;
		padding-top: 50px;

		width: 100vw;
		height: 100vh;

	}

	#tableWrapper{
		max-height: 125px;
		overflow-y: scroll;
	}

	.table {
		background: transparent;
		border: none;

	}
	.table, tr, td {
		border:none !important;
		padding-bottom: 0px;
		margin-bottom: 0px;
	}

	#formHeader {
		font-family: 'overpass-bold', serif;
		font-size: 30px;
		font-weight: 300;

		margin-top: 10px;
		padding-left: 5%;
		padding-bottom: 20px;
	}

	.FormStep {
		margin-left: 5%;
		margin-right: 5%;
		padding-bottom: 20px;
		border-bottom: solid darkgray 1px;
	}
	.formTitle {
		padding-top: 10px;
		padding-bottom: 10px;
		margin-bottom: 10px;
		font-family: 'overpass-bold';
		font-size: 20px;

	}

	#dataInput-title {
		margin: none;
		flex:1;
	}
	.formInput {
		position: relative;
		width: auto;
		padding-left: 10px;
		padding-right: 10px;

		background:none;
		border: 2px gray;
	}
	.fileInput {
		width: 30%;
		height: 0.1px;
		opacity: 0;

		overflow: hidden;
		text-overflow: ellipsis;
		position: absolute;


	}
	.fileInput + label {
		border: 1px solid lightgray;
		background-color: white;
		border-radius: 3px;
		padding-left: 10px;
		padding-right: 10px;
		padding-top: 5px;
		padding-bottom: 5px;
    display: inline-block;
	}

	.fileInput:hover + label,
	.fileInput + label:hover {
			background-color: lightgray;
	}
	.fileInput + label {
		cursor: pointer; /* "hand" cursor */
	}
	input[type="text"], textarea, input[type="file"] {
		outline: none;
		background:transparent;

		font-size: 14px;
		border: 1px solid gray;
		border-radius: 3px;

		padding-left: 10px;

		width: 100%;
		height:35px;

	}

	#dataInput-addSet{
		padding: 10px;
	}
	#dataInput-inputs{
		display: flex;
		justify-content: left;

		width: 100%;
		height: auto;
	}

	.dataInput-input{
		width: 30%;
		height: auto;
		margin: 0px auto;

		position: relative;

	}
	#submitButton {
		display:flex;
		justify-content: left;

	}
	@media (min-width: 768px) {
		#formwrapper {
			left: 15vw;
			right:15vw;
			top:15vh;
			bottom:15vh;
		}
		.dataInput-top {
			display: flex;
		}
	}


</style>



<script type="text/javascript">
	import axios from 'axios'

	export default {

		name: 'InputFiles',
		data() {
			return {
				userData: {
				  sparkURL: ""
				},
				dataRows: [{endpoint: "", container: "", dataset: ""}],
				jobStatus: ""
			}
		},
		methods: {
			submitData()
			{
				// submit user data

				const response =
				  {
				  	// TODO: add functionality to upload protocol
				  	"protocol": {},
					"config":
					  {
					  	"userData": this.userData,
							"dataRows": this.dataRows
					  }
				  };

				const path = "/api/submit";

				axios.post(path, response)
				  .then(function(response){console.log(response);})
				  .catch(function(error){console.log(error);});
			},
			onFileChange(e){
				var files = e.target.files || e.dataTransfer.files;
				var label = e.target.nextElementSibling;

				if (files.length != undefined && files.length != 0)
					if (files.length > 1)
						label.textContent = 'Uploaded ' + files.length + ' files';
					else
						label.textContent = files[0].name;
			},
			handleSubmit()
			{
				// idk what this is. if i remove it things break
			},
			removeData(id)
			{
				const index = this.dataRows.findIndex(item => item.id === id);
				this.dataRows.splice(index, 1);
			},
			addData()
			{
				var elem = document.createElement('tr');
				this.dataRows.push({
					id: Math.random().toString(32).slice(2, 10), // replace me
				  endpoint: "",
				  container: "",
				  dataset: ""
				});
			},
			getStatusFromBackend()
			{
				const path = '/api/job_status';
				axios.get(path)
				  .then(response => {
				  	this.jobStatus = response.data.status
				  })
				  .catch(error => {
				  	console.log(error)
					})

			}
		}
	}
</script>
