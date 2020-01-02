<template>
  <div class="col-xs-12 col-sm-8 col-sm-offset-2 col-md-6 col-md-offset-3 col-lg-4 col-lg-offset-4">
    <p>Status: {{connStatus}}</p>
    <p>Heart Rate: {{heartRateValue}} @ {{heartRateTime}}</p>
  </div>
</template>

<script>

import io from 'socket.io-client'
// import Rickshaw from 'rickshaw'
import 'rickshaw/rickshaw.min.css'

var socket = io.connect('http://localhost:3000')

export default {
  name: 'home',
  data () {
    return {
      connStatus: 'Disconnected',
      heartRateValue: '-',
      heartRateTime: '-'
    }
  },
  mounted () {
    this.openSocketListeners()
  },
  methods: {
    openSocketListeners () {
      socket.on('connect', () => {
        this.$log.debug('Socket status: Connected')
        this.connStatus = 'Connected'
      })

      socket.on('disconnect', () => {
        this.$log.debug('Socket status: Disconnected')
        this.connStatus = 'Disconnected'
      })

      socket.on('TrackBossHRM', (data) => {
        this.$log.debug('Socket received (data): %o', data)
        this.heartRateValue = data.heart_rate
        this.heartRateTime = data.time
      })
    }
  }
}

</script>

<style scoped>

</style>
