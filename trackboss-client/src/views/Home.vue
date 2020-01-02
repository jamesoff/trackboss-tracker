<template>
  <div class="home">
    <img alt="DeepRacer logo" src="../assets/deepracer-logo.png" width="200">
    <Home/>
  </div>
</template>

<script>
// @ is an alias to /src
import Home from '@/components/Home.vue'

export default {
  name: 'home',
  components: {
    Home
  }
}
</script>
