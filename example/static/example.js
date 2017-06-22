var JsonApi = require('devour-client');

var jsonApi = new JsonApi({
  apiUrl: 'http://localhost:8888/api',
  trailingSlash: {resource: false, collection:true}
});

jsonApi.define('application', {
  name: ''
});

jsonApi.create('application', {
  name: 'Mayavi'
})
.then(function() {
  jsonApi.findAll('applications').then(function(result) {
    console.log(result);
  });
});
