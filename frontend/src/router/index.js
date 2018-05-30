import Vue from 'vue'
import Router from 'vue-router'
import home from '@/components/Home'
import about from '@/components/About'

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Home',
      component: home
    },
    {
      path: '/about',
      name: 'About',
      component: about
    },
  ],
  mode: 'history',
  linkActiveClass: 'is-active'
})
