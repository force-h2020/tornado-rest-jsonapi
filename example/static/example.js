var JsonApi = require('devour-client');

var jsonApi = new JsonApi({
  apiUrl: 'http://localhost:8888/api',
  trailingSlash: {resource: true, collection:true}
});

jsonApi.define('application', {
  name: ''
});

jsonApi.create('application', {
  name: 'Mayavi'
})
.then(function(result) {
  console.log('Mayavi id:', result);

  jsonApi.find('application', 0).then(function(result) {
    console.log('application 0:', result);

    jsonApi.create('application', {
      name: 'Jupyter Notebook'
    })
    .then(function(result) {
      console.log('Jupyter Notebook id:', result);

      jsonApi.findAll('applications').then(function(result) {
        console.log('applications:', result);

        jsonApi.destroy('application', 0).then(function() {
          jsonApi.findAll('applications').then(function(result) {
            console.log('applications:', result);
          });
        });
      });
    });
  });
});
