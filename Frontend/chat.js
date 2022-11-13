var checkout = {};

$(document).ready(function() {

  function callChatbotApi(message) {
    var params = {
      'q' : message
  };
    return sdk.searchGet(params, {}, {});
  }
  function uploadPhoto()
  {
    var filePath = (document.getElementById('uploaded_file').value).split("\\");
    var fileName = filePath[filePath.length - 1];
    var customLabels=document.getElementById('custom_labels').value;
      console.log(fileName);
      console.log(custom_labels.value);
      var reader = new FileReader();
    var file = document.getElementById('uploaded_file').files[0];
    reader.onload = function (event) {
      body = btoa(event.target.result);
      console.log('Reader body : ', body);
      
        var params = {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers':'*',
          'Content-Type': 'image/jpeg'+";"+customLabels,
          'bucket':"photoalbumassignment",
          'key':fileName,
          'Accept':'*/*',
          'x-amz-meta-customLabels':'Person'
        };
      sdk.uploadBucketKeyPut(params, body,{})
      .then(function(result) {
          console.log(result);
      })
      .catch(function(error) {
          console.log(error);
      })
  }
  reader.readAsBinaryString(file);
  }

  function insertMessage() {
    msg = $('#transcript').val();
    if ($.trim(msg) == '') {
      return false;
    }
    
    callChatbotApi(msg)
      .then((response) => {
        console.log(response.data);
        var data=response.data;
        var ele=document.getElementById("photosearch");
        ele.innerHTML="";
        var n;
        if(response.data=='No Results found')
        {
          return;
        }
        for (n = 0; n < data.length; n++) {
          console.log(data[n]);
            ele.innerHTML += '<figure><img src="' + ("https://photoalbumassignment.s3.us-east-1.amazonaws.com/"+data[n]) + '" style="width:25%"></figure>';
        }
      })
      .catch((error) => {
        console.log('an error occurred', error);
      });
  }
  

  $('#search').click(function() {
    insertMessage();
  });

  $('#upload_files').click(function() {
    uploadPhoto()
  });

});
