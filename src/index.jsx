window.jQuery = require('jquery');
window.$ = jQuery;
window.Tether = require('tether');
window.bootstrap = require('bootstrap');
// var _ = require('lodash');
// var Rickshaw = require('rickshaw');
// var d3 = require('d3js');
// var nvd3 = require('nvd3js');
// var moment = require('moment');
// require('datejs');
// require('select2');


import React from 'react';
import { render } from 'react-dom';
import 'react-bootstrap';

class StorePicker extends React.Component {
  render() {
    // Any where else
    return <p>Hello There World!</p>
  }
}

render(<StorePicker/>, document.querySelector('#main'));