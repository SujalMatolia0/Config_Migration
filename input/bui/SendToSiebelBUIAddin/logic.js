//This js file creates a new SR and paases the control to askForSiebelNumber.js in case of adding to an existing SR
var incident_id = 0;
var siebel_srnumber, create_time, interface_Url, session_id, log_message;
var stopsave = false;
log_Messages("trace", "Started Execution");
ORACLE_SERVICE_CLOUD.extension_loader.load("SEND_TO_SIEBEL", "1").then(function (extensionProvider) {
  extensionProvider.registerWorkspaceExtension(function (WorkspaceRecord) {
    wRecord = WorkspaceRecord;
    wRecord.getFieldValues(['Incident.IId', 'Incident.C$siebel_sr_number', 'Incident.Created']).then(function (IFieldDetails) {
      siebel_srnumber = IFieldDetails.getField('Incident.C$siebel_sr_number').getValue();
      create_time = IFieldDetails.getField('Incident.Created').getValue();
      create_time = create_time ? new Date(create_time).toISOString().replace(/\.\d{3}Z$/, 'Z') : '';
      incident_id = IFieldDetails.getField('Incident.IId').getValue();
      //console.log(" incident record id is", incident_id, "create_time is ", create_time);
      //In case of a new Incident
      if (incident_id < 1) {
        WorkspaceRecord.addRecordSavedListener(function () {
          incident_id = WorkspaceRecord.getWorkspaceRecordId();
          wRecord.getFieldValues(['Incident.Created']).then(function (IFieldDetails) {
            create_time = IFieldDetails.getField('Incident.Created').getValue();
            create_time = create_time ? new Date(create_time).toISOString().replace(/\.\d{3}Z$/, 'Z') : '';
          });
        });
      }
      log_message = "Incident Id: " + incident_id + " create_time is " + create_time;
      log_Messages("info", log_message);
    });
    wRecord.addFieldValueListener('Incident.C$siebel_sr_number', updateSrNumberChange);
  });
});

$(document).ready(function () {
  $("#new_siebel_button").click(function () {
    triggerSendToSiebel();
  });
  $("#existing_siebel_button").click(triggerExistingSiebel);
});

function updateSrNumberChange(parameter) {
  siebel_srnumber = parameter.event.value;
  triggerSuccessMsg(siebel_srnumber);
}

function triggerSendToSiebel() {
  try {
    log_Messages("trace", "Triggered the function");
    log_message = "Incident Id: " + incident_id + " create_time is " + create_time + " siebel_srnumber is " + siebel_srnumber + "new_siebel_srnumber is: ";
    log_Messages("info", log_message);
    //console.log(log_message);
    if (incident_id < 1)
      alert("Please save the incident before attempting to send to Siebel.");
    else if (siebel_srnumber)
      alert("Error: There is already an SR associated with the Incident.");
    else {
      //This makes sure that latest info on the Incident is saved and will be picked by the model file while sending the info to the Siebel
      wRecord.executeEditorCommand('Save',
        function () {
          var error_number = "";
          var error_string = "";
          var newsielbelnumber = "";
          //to fetch session details from AuthLibraryExtn.js library add-in
          myAuthentication.then(function (value) {
            var postdata = "incident_info=" + encodeURIComponent(JSON.stringify({
              "incident_id": incident_id,
              "siebel_sr_number": "",
              "token": create_time
            }));
            log_message = "PostData from triggerSendToSiebel function for new SR is" + postdata;
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
                    siebel_srnumber = newsielbelnumber;
                    wRecord.updateField('Incident.c$siebel_sr_number', siebel_srnumber);
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
                    log_message = "warning from triggerSendToSiebel function else block is " + error_string;
                    log_Messages("warn", log_message);
                  }
                }
              },
              error: function (xhr, status, error) {
                console.error('Error: ', error);
                log_message = "error from triggerSendToSiebel function catch block is " + error;
                log_Messages("error", log_message);
              }
            });
          });
        });
    }
  }
  catch (error) {
    console.error("Error in triggerSendToSiebel function :", error);
    log_Messages("error", "API error in triggerSendToSiebel function for incident: " + incident_id + " error: " + error);
  }
}

function triggerExistingSiebel() {
  ORACLE_SERVICE_CLOUD.extension_loader.load("SEND_TO_SIEBEL", "1").then(function (extensionProvider) {
    extensionProvider.registerUserInterfaceExtension(function (IUserInterfaceContext) {
      IUserInterfaceContext.getModalWindowContext().then(function (IModalWindowContext) {
        var modalWindow = IModalWindowContext.createModalWindow();
        modalWindow.setTitle("Siebel SR Number");
        modalWindow.setContentUrl("/askForSiebelNumber.html");
        modalWindow.setHeight('150px');
        modalWindow.setWidth('300px');
        modalWindow.render();
      });
    });
  });
}

function triggerSuccessMsg(siebel_num) {
  ORACLE_SERVICE_CLOUD.extension_loader.load("SEND_TO_SIEBEL", "1").then(function (extensionProvider) {
    extensionProvider.registerUserInterfaceExtension(function (IUserInterfaceContext) {
      IUserInterfaceContext.getModalWindowContext().then(function (IModalWindowContext) {
        var modalWindow = IModalWindowContext.createModalWindow();
        modalWindow.setTitle("");
        modalWindow.setContentUrl("/successMessage.html?siebel_num=" + siebel_num);
        modalWindow.setHeight('100px');
        modalWindow.setWidth('250px');
        modalWindow.render();
      });
    });
  });
}