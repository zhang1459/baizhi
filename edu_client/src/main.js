import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'
import "./static/css/global.css"
Vue.prototype.$axios = axios;

import Element from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import VideoPlayer from 'vue-video-player'
Vue.use(Element);
Vue.config.productionTip = false

import settings from "./settings"
Vue.prototype.$settings = settings;
import "./static/js/gt"

require('video.js/dist/video-js.css')
require('vue-video-player/src/custom-theme.css')
Vue.use(VideoPlayer)
new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
