<template>
  <div id="contact">

    <img class = 'contact-image' v-bind:src= "profileURL" />
    
    <div id="contact-description">
      <div id="contact-name">
        <p>{{ author }}</p>
      </div>
      <div id="contact-title">
        <p>{{ title }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    profileURL: String,
    author: String,
    title: String
  },

  data: function() {
    return {
      
    };
  }
}
</script>

<style>
  #contact {
    padding-top: 20px;
    position:relative;
    color: black;
    display:flex;
    justify-content: left;
    text-align: left;
  }
  .contact-image{
    width: 50px;
    height: 50px;
  }
  #contact-name{
    font-size: 18px;
  }
   
  #contact-title {
    font-size: 12px;
  }
  #contact-description{
    display:flex;
    flex-direction: column;
    justify-content: top;
  }
  
</style>





