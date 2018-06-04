<!DOCTYPE html>
<template>
  <div id="home">
      <form @submit.prevent="handleSubmit">
          <div class="columns">
              <div class="column">
                  <table class="table is-bordered">
                      <thead>
                        <td>
                            <strong>Step 1 - Input Party ID and Spark Master URL.</strong>
                        </td>
                      </thead>
                      <tr>
                          <td>
                              <strong>Your Party ID</strong>
                              <input type="text" v-model="userData.partyId">
                          </td>
                      </tr>
                      <tr>
                          <td>
                              <strong>Spark Master URL</strong>
                              <input type="text" v-model="userData.sparkURL">
                          </td>
                      </tr>
                  </table>
              </div>
          </div>
          <div class="columns">
              <div class="column">
                      <table class="table is-bordered">
                          <thead>
                              <td>
                                  <strong>Step 2 - Specify Your Input Datasets.</strong>
                              </td>
                              <td>
                                  <button class="button is-centered" @click="addData">Add A Dataset</button>
                              </td>
                          </thead>
                          <thead>
                          <tr>
                              <td>
                                  <strong>Endpoint</strong>
                              </td>
                              <td>
                                  <strong>Container</strong>
                              </td>
                              <td>
                                  <strong>Dataset</strong>
                              </td>
                              <td></td>
                          </tr>
                          </thead>
                          <tbody>
                          <tr v-for="(row, index) in dataRows">
                              <td>
                                  <input type="text" v-model="row.endpoint">
                              </td>
                              <td>
                                  <input type="text" v-model="row.container">
                              </td>
                              <td>
                                  <input type="text" v-model="row.dataset">
                              </td>
                              <td>
                                  <a v-on:click="removeData(index)" style="cursor: pointer">Remove</a>
                              </td>
                          </tr>
                          </tbody>
                      </table>

                  <div class="columns">
                      <div class="column">
                          <table class="table is-bordered">
                              <thead>
                              <td>
                                  <strong>Step 3- Submit!</strong>
                              </td>
                              </thead>
                          </table>
                          <button class="button btn-primary is-pulled-left" type="submit" @click="submitData">Compute</button>
                          <button class="button btn-primary is-pulled-right" @click="getStatusFromBackend">Check Status</button>
                          <p>Job Status:  {{ jobStatus }} </p>
                      </div>
                  </div>
              </div>
          </div>
      </form>
  </div>
</template>

<script type="text/javascript">
    import axios from 'axios'

	export default {
		name: 'InputFiles',
		data() {
			return {
				userData: {
                  partyId: "",
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
            		"userData": this.userData,
                    "dataRows": this.dataRows
                  };

                const path = "http://localhost:5000/api/job_submit";

                axios.post(path, response)
                  .then(function(response){console.log(response);})
                  .catch(function(error){console.log(error);});
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
              var elem = document.createElement('tr');
                this.dataRows.push({
                  endpoint: "",
                  container: "",
                  dataset: ""
                });
			},
            getStatusFromBackend()
            {
				const path = 'http://localhost:5000/api/job_status';
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

<style lang='css'>
    @import '../../node_modules/bulma/css/bulma.css';
    #home {
        font-family: 'Avenir', Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-align: center;
        margin-top: 50px;
    }
    .table thead {
        -moz-border-radius: 10px;
        background-color: rgba(255, 39, 37, 0.14);
    }
</style>
