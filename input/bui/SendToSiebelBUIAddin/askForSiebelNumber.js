//This js file adds the incident to an existing SR
const siebelNumberInput = document.getElementById("siebel_number");
const submitBtn = document.getElementById("submit_btn");
siebelNumberInput.addEventListener("input", function () {
  submitBtn.disabled = this.value.trim() === "";
});

document.getElementById('submit_btn').addEventListener('click', submit);

document.getElementById('cancel_btn').addEventListener('click',
  function () {
    closeModalWindow();
  });

function closeModalWindow() {
  ORACLE_SERVICE_CLOUD.extension_loader.load("CUSTOM_APP_ID", "1")
    .then(function (extensionProvider) {
      extensionProvider.registerUserInterfaceExtension(function (IUserInterfaceContext) {
        IUserInterfaceContext.getModalWindowContext().then(function (IModalWindowContext) {
          IModalWindowContext.getCurrentModalWindow().then(function (IModalWindow) {
            if (IModalWindow) {
              IModalWindow.close();
            }
          });
        });
      });
    });
}
function submit() {
  var new_siebel_srnumber = document.getElementById('siebel_number').value;

  ORACLE_SERVICE_CLOUD.extension_loader.load("SEND_TO_SIEBEL", "1").then(function (extensionProvider) {
    extensionProvider.registerWorkspaceExtension(function (WorkspaceRecord) {
      wRecord = WorkspaceRecord;
      //This makes sure that latest info on the Incident is saved and will be picked by the model file while sending the info to the Siebel
      wRecord.executeEditorCommand('Save',
        function () {
          var error_number = "";
          var error_string = "";
          var newsielbelnumber = "";
          var srnum = new_siebel_srnumber;
          //to fetch session details from AuthLibraryExtn.js library add-in
          myAuthentication.then(function (value) {
            var postdata = "incident_info=" + encodeURIComponent(JSON.stringify({
              "incident_id": incident_id,
              "siebel_sr_number": srnum,
              "token": create_time
            }));
            log_message = "PostData from triggerSendToSiebel function for adding an existing new SR is" + postdata;
            log_Messages("info", log_message);
            //console.log(log_message);
            //Sending Incident details to siebel via an existing CP controller file which is already being used in .net add-in
            var result = $.ajax({
              type: "POST",
              headers: {
                "Authorization": "Session " + sessionID
              },
              url: interfaceUrl + '/cc/ajaxCustom/addSrToSiebel',
              contentType: "application/x-www-form-urlencoded",
              data: postdata,
              async: false,
              success: function (response) {
                closeModalWindow();
                //console.log('Success:', response);
                log_Messages("info", "Ajax response: " + response);
                var responseData = JSON.parse(response);
                if (Array.isArray(responseData) && responseData.length > 0) {
                  var item = responseData[0];
                  error_number = item.error_number;
                  error_string = item.error_string;
                  newsielbelnumber = item.sr_number;
                  //console.log("Error Number:", error_number, "Error String:", error_string, "SR Number:", newsielbelnumber);
                  if (newsielbelnumber && (!error_number || error_number == "0")) {
                    wRecord.updateField('Incident.c$siebel_sr_number', newsielbelnumber);
                    wRecord.executeEditorCommand('Save');
                  }
                  else if (error_number == "700") {
                    alert('Unable to submit SR. The Siebel webservice is unavailable. Please contact IS at x7747.');
                  }
                  else {
                    var text = "Error Adding SR:\n" +
                      "Error Code(s): " + error_number + "\n" +
                      "Error String(s): " + error_string + "\n" +
                      "SR Number(s):";
                    alert(text);
                    log_message = "warning from triggerSendToSiebel function else block is " + text;
                    log_Messages("warn", log_message);
                  }
                }
              },
              error: function (xhr, status, error) {
                closeModalWindow();
                console.log('Error: ', error);
                log_message = "error from triggerSendToSiebel function catch block is " + error;
                log_Messages("error", log_message);
              }
            });
          });
        });
    });
  });
}