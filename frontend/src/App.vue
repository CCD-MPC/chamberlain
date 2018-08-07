<template>
  <div id="app">
    <nav id = 'navbar'>
      <div class="navbar-logo">
        <img id = 'icon' src = '../assets/blueHatCICI.png'>
      </div>
      <div id="navbar-items" role='navigation' aria-label='main navigation'>
        <div id="navbar-itemWrapper"> 
          <div class="linkWrapper">
            <router-link id="navbar-item" to="/" exact>
              Home
            </router-link>
          </div>
          <div class="linkWrapper">
            <router-link id="navbar-item" to="/about" >
              About
            </router-link>
          </div>
        </div>
      </div>
    </nav>
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'app'
}
</script>

<style lang='css'>
  @import url('https://fonts.googleapis.com/css?family=Overpass:300,400');

  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    overflow-y: scroll;
  }
  #icon {
    height:40px;
  }
  
  #navbar {
    background-color: #030303; 
    display: flex;
    color:#0088ce;
  }
  
  #navbar-items{
   
    display:flex;
    justify-content:right;
    margin-left: auto;
  }

  #navbar-itemWrapper{
    flex-grow: 1;
    display: flex;
    
  }
  .linkWrapper{
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  #navbar-item{
    font-family: 'overpass-bold';
    
    padding-left: 10px;
    padding-right: 10px;
  }
  #navbar-item:focus{
    color: #00659c;
  }


</style>
