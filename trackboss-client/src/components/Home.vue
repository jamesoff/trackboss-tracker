<template>
  <div class="row text-center">
    <div class="col-xs-12 col-sm-12 col-md-12 col-lg-12">
      <!-- Panel div start -->
      <div class="panel panel-primary">
        <div class="panel-heading">
          <h1>Trackboss Tracker</h1>
        </div>
        <div class="panel-body">
          <!-- Chart container -->
          <div id="chart_container" >
            <div id="y_axis"></div>
            <div id="chart" ref="panel"></div>
          </div>
          <!-- End of chart container -->
        </div>
      </div>
      <!-- Panel div end -->
    </div>
    <div class="col-xs-12 col-sm-12 col-md-12 col-lg-12">
      <img alt="DeepRacer logo" src="../assets/deepracer-logo.png" width="200">
      <p>Status: {{connStatus}}</p>
      <!-- <p>{{message}}</p>
      <h3>Trackboss info</h3>
      <p>Trackboss Age: <input v-model="tbAge" placeholder=""></p>
      <p>Trackboss Resting Heart Rate: <input v-model="tbRestingHR" placeholder=""></p>
      <p><a @click="calculateHRZones">Update HR Zones</a></p> -->
      <!-- <h3>Trackboss HR zones</h3> -->
      <h1>Current HR: {{heartRateValue}}</h1>
      <p>@ {{heartRateTime}}</p>
      <!-- <p>Max HR: {{tbMaxHR}}</p>
      <p>Aerobic Threshold: {{tbAerobicHR}}</p>
      <p>Fat burning threshold: {{tbFatHR}}</p> -->
    </div>
  </div>
</template>

<script>

import io from 'socket.io-client'
import Rickshaw from 'rickshaw'
import moment from 'moment'
import 'rickshaw/rickshaw.min.css'

var socket = io.connect('http://localhost:3000')
var hrmChart

export default {
  name: 'home',
  data () {
    return {
      connStatus: 'Disconnected',
      message: '',
      heartRateValue: '-',
      heartRateTime: '-',
      timeInterval: 1000,
      tbAge: 0,
      tbRestingHR: 0,
      tbFatHR: 0,
      tbAerobicHR: 0,
      tbMaxHR: 220
    }
  },
  mounted () {
    this.initChart()
    this.openSocketListeners()
    this.colorPalette()
  },
  methods: {
    initChart () {
      hrmChart = new Rickshaw.Graph({
        element: document.getElementById('chart'),
        width: 900,
        height: 1200,
        renderer: 'line',
        min: 0,
        max: 200,
        series: new Rickshaw.Series.FixedDuration([{
          name: 'hr', color: 'red'
        }], undefined, {
          timeInterval: this.timeInterval,
          maxDataPoints: 100,
          timeBase: new Date().getTime() / 1000
        })
      })

      /* eslint-disable no-unused-vars */
      var xAxis = new Rickshaw.Graph.Axis.X({
        graph: hrmChart,
        ticks: 9,
        tickFormat: function (x) {
          return moment(Date(x)).format('HH:mm:ss')
        }
      })
      xAxis.render()

      var yAxis = new Rickshaw.Graph.Axis.Y({
        graph: hrmChart,
        orientation: 'left',
        element: document.getElementById('y_axis')
      })
      yAxis.render()

      /* eslint-disable no-unused-vars */
      // var hoverDetail = new Rickshaw.Graph.HoverDetail({
      //   graph: hrmChart,
      //   formatter: function (series, x, y) {
      //     var date = '<span class="date">' + new Date(x * 1000).toUTCString() + '</span>'
      //     var content = series.name + ': ' + parseInt(y) + '<br>' + date
      //     return content
      //   }
      // })
      // hrmChart.render()
    },
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

        var graphData = { hr: this.heartRateValue }

        hrmChart.series.addData(graphData)
        // hrmChart.series[0] = ''
        // this.$log.debug('series: %o', hrmChart.series[0])
        hrmChart.render()
      })
    },
    calculateHRZones () {
      this.$log.debug('here')
      if ((this.tbAge > 18 && this.tbAge < 60) && (this.tbRestingHR > 40 && this.tbRestingHR < 100)) {
        this.tbMaxHR = 220 - Number(this.tbAge)

        var reserveHR = this.tbMaxHR - this.tbRestingHR
        this.tbFatHR = Number(this.getPercentage(reserveHR, 50)) + Number(this.tbRestingHR)
        this.tbAerobicHR = Number(this.getPercentage(reserveHR, 25)) + Number(this.tbRestingHR)

        this.$log.debug('tbMaxHR: %s', this.tbMaxHR)
        this.$log.debug('tbAerobicHR: %s', this.tbAerobicHR)
        this.$log.debug('tbFatHR: %s', this.tbFatHR)
      }
    },
    getPercentage (num, percent) {
      return Math.floor(Number(num) - ((Number(percent) / 100) * Number(num)))
    },
    colorPalette () {
      this.$log.debug('screen: %s', this.$route.query.screen)
    }
  }
}

</script>

<style scoped>

#chart_container {
  padding-right: 40px;
  padding-bottom: 20px;
  margin-top: 20px;
  position: relative;
}

#chart {
  position: relative;
  left: 40px;
}

#y_axis {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 40px;
}

h1 {
  font-size: 48pt;
}

/* .rickshaw_graph .y_ticks text {
   fill: #fff;
}

.rickshaw_graph .x_tick .title {
   color: #fff;
} */

</style>
