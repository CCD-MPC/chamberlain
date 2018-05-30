<template>
  <div id="app">
    <nav class="navbar-menu" role="navigation" aria-label="main navigation" >
      <div class="navbar-start is-bordered">
          <router-link class="navbar-item" to="/">
          Home
          </router-link>
          <router-link class="navbar-item" to="/about">
              About
          </router-link>
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
  @import '../node_modules/bulma/css/bulma.css';
    #app {
      font-family: 'Avenir', Helvetica, Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-align: center;
      color: #2c3e50;
    }
    .navbar-menu {
        -moz-border-radius: 10px;
        background-color: rgba(255, 39, 37, 0.18);
    }
</style>
