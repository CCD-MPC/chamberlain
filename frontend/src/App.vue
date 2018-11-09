<template>
  <div id="app">
    <nav id = 'navbar'>
      <div class="navbar-logo">
        <img id = 'icon' src = '../assets/blueHatCICI.png'>
      </div>
      <div id="navbar-items" role='navigation' aria-label='main navigation'>
        <div id="navbar-itemWrapper">
          <div class="linkWrapper">
            <router-link class="navbar-item" to="/" exact>
                Home
            </router-link>
          </div>
          <div class="linkWrapper">
            <router-link class="navbar-item" to="/about" exact>
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

  @font-face {
    font-family: 'overpass-light';
    src: url('../assets/overpass-light.otf');
  }

  #app {
    font-family: 'overpass-light', Helvetica, Arial, sans-serif;
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
      padding-left: 10px;
      padding-right: 10px;
  }
  .navbar-item{
    font-family: 'overpass-light';
    padding-left: 10px;
    padding-right: 10px;
  }
  #navbar-item:focus{
    color: #00659c;
  }

</style>
