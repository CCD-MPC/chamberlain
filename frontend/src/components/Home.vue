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
                            <tbody>
                            <tr v-for="(row, index) in dataRows">
                                <td>
                                    <input type="text" v-model="row.alias">
                                </td>
                                <td>
                                    <input type="text" v-model="row.doi">
                                </td>
                                <td>
                                    <input type="text" v-model="row.files">
                                </td>
                                <td>
                                    <a v-on:click="removeData(index)" style="cursor: pointer">Remove</a>
                                </td>
                            </tr>
                            </tbody>
						</table>
					</div>
				</div>
              <div class="FormStep" id="submit">
                  <div class="formTitle">
                      <h1>Step 2: Upload a Protocol & Submit</h1>
                  </div>
                  <div id="protocolButton">
                      <input style = 'margin-left: 10px' class="button is-pulled-left" id="protocol" type="file" @change="onFileChange">
                  </div>
                  <div id = 'submitButton'>
                      <button style = 'margin-left: 10px' class="button" type="submit" @click="submitData">Compute</button>
                      <div> Your Compute ID: {{ ID }}</div>
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

    var contents;

	export default {

		name: 'InputFiles',
		data() {
			return {
				dataRows: [{alias: "", doi: "", files: ""}],
                jobStatus: "",
                ID: "",
                protocol: ""
			}
		},
		methods: {
			submitData()
			{
              new Date;
              var ID = Date.now();

              this.ID = ID;

              const response =
                {
                  "protocol": contents,
                  "ID": ID,
                  "config":
                    {
                      "dataRows": [],
                      "dataverse": this.dataRows
                    }
                };

              const path = "/api/submit";

              axios.post(path, response)
                .then(function(response){console.log(response);})
                .catch(function(error){console.log(error);});

			},
			onFileChange(e){
				const file = e.target.files[0];
				const reader = new FileReader();

				reader.onload = function(e) {
					contents = e.target.result;
                    return contents;
                };

				reader.readAsText(file);

			},
			handleSubmit()
			{
				// idk what this is. if i remove it things break
			},
			removeData(index)
			{
              this.dataRows.splice(index, 1);
			},
			addData()
			{
              this.dataRows.push({
                endpoint: "",
                container: "",
                dataset: ""
              });
			},
			getStatusFromBackend()
			{
              const path = '/api/job_status';

              const response =
                {
                  "ID": this.ID
                };

              axios.post(path, response)
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
