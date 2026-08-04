# BUI Add-In: `SendToSiebelBUIAddin`

- **Add-In Name**: `SendToSiebelBUIAddin`
- **Extension Type**: `BUIAddin`
- **Entry Point**: `init.html`
- **Total Package Files**: 5
- **Risk Findings Count**: 6

---

## Package Structure & Extracted Web Assets

| Asset Filename | Asset Type | Notes |
|---|---|---|
| `askForSiebelNumber.html` | `html` | HTML Modal View / UI Page |
| `askForSiebelNumber.js` | `js` | JavaScript Application Logic |
| `init.html` | `html` | Extension Entry Point |
| `logic.js` | `js` | JavaScript Application Logic |
| `successMessage.html` | `html` | HTML Modal View / UI Page |

### HTML Live Previews

#### HTML Asset: `init.html`

<div class="html-preview-pending" data-html="PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVuIj4KCjxoZWFkPgogIDxtZXRhIGNoYXJzZXQ9IlVURi04Ij4KICA8bWV0YSBuYW1lPSJ2aWV3cG9ydCIgY29udGVudD0id2lkdGg9ZGV2aWNlLXdpZHRoLCBpbml0aWFsLXNjYWxlPTEuMCI+CiAgPHRpdGxlPlNlbmQgdG8gU2llYmVsPC90aXRsZT4KICA8c3R5bGU+CiAgICAuYnV0dG9uLWNvbnRhaW5lciB7CiAgICAgIGRpc3BsYXk6IGZsZXg7CiAgICAgIGp1c3RpZnktY29udGVudDogY2VudGVyOwogICAgICBtYXJnaW4tdG9wOiAyMHB4OwogICAgfQoKICAgIC5jdXN0b20tYnV0dG9uIHsKICAgICAgYmFja2dyb3VuZC1jb2xvcjogIzJkNDE5YTsKICAgICAgY29sb3I6IHdoaXRlOwogICAgICBib3JkZXI6IG5vbmU7CiAgICAgIHBhZGRpbmc6IDE1cHg7CiAgICAgIGJvcmRlci1yYWRpdXM6IDEycHg7CiAgICAgIGhlaWdodDogNjVweDsKICAgICAgd2lkdGg6IDE4MHB4OwogICAgICBjdXJzb3I6IHBvaW50ZXI7CiAgICAgIGRpc3BsYXk6IGZsZXg7CiAgICAgIGp1c3RpZnktY29udGVudDogY2VudGVyOwogICAgICBhbGlnbi1pdGVtczogY2VudGVyOwogICAgICBtYXJnaW4tcmlnaHQ6IDEwcHg7CiAgICB9CgogICAgLmN1c3RvbS1idXR0b246aG92ZXIgewogICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjMjVhYWVhOwogICAgfQogIDwvc3R5bGU+CjwvaGVhZD4KCjxib2R5PgogIDxkaXYgY2xhc3M9ImJ1dHRvbi1jb250YWluZXIiPgogICAgPGJ1dHRvbiBpZD0ibmV3X3NpZWJlbF9idXR0b24iIGNsYXNzPSJjdXN0b20tYnV0dG9uIj5BZGQgTmV3IFNpZWJlbCBTUjwvYnV0dG9uPgogICAgPGJ1dHRvbiBpZD0iZXhpc3Rpbmdfc2llYmVsX2J1dHRvbiIgY2xhc3M9ImN1c3RvbS1idXR0b24iPkFkZCB0byBFeGlzdGluZyBTaWViZWwgU1I8L2J1dHRvbj4KICA8L2Rpdj4KCiAgPCEtLSBBZGQgeW91ciBzY3JpcHRzIGJlbG93IHRoaXMgbGluZSAtLT4KICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9hamF4Lmdvb2dsZWFwaXMuY29tL2FqYXgvbGlicy9qcXVlcnkvMy41LjEvanF1ZXJ5Lm1pbi5qcyI+PC9zY3JpcHQ+CiAgPHNjcmlwdCBzcmM9Imh0dHBzOi8vY29kZS5qcXVlcnkuY29tL2pxdWVyeS0zLjYuMC5taW4uanMiPjwvc2NyaXB0PgogIDxzY3JpcHQgc3JjPSJodHRwczovL2NvZGUuanF1ZXJ5LmNvbS91aS8xLjEyLjEvanF1ZXJ5LXVpLmpzIj48L3NjcmlwdD4KICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvanNwZGYvMS41LjEvanNwZGYubWluLmpzIj48L3NjcmlwdD4KICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvanNwZGYtYXV0b3RhYmxlLzMuMi40L2pzcGRmLnBsdWdpbi5hdXRvdGFibGUubWluLmpzIj48L3NjcmlwdD4KICA8bGluayByZWw9InN0eWxlc2hlZXQiIGhyZWY9Ii8vY29kZS5qcXVlcnkuY29tL3VpLzEuMTIuMS90aGVtZXMvYmFzZS9qcXVlcnktdWkuY3NzIj4KCiAgPHNjcmlwdCBzcmM9Ii4uLy4uL0F1dGhMaWJyYXJ5RXh0bi9BdXRoTGlicmFyeUV4dG4uanMiPjwvc2NyaXB0PgogIDwhLS1UaGlzIGlzIGxpYnJhcnkgYWRkLWluIHVzZWQgdG8gZmV0Y2ggc2Vzc2lvbiBhbmQgb3RoZXIgYXBwbGljYXRpb24gZGV0YWlscy0tPgogIDxzY3JpcHQgdHlwZT0idGV4dC9qYXZhc2NyaXB0IiBzcmM9ImxvZ2ljLmpzIj48L3NjcmlwdD4KICA8IS0tVGhpcyBoYXMgbG9naWMgdG8gc2VuZCBJbmNpZGVudCBkZXRhaWxzIHRvIFNpZWJlbCBmb3IgY3JlYXRpbmcgYSBOZXcgU1Igb3IgYXNzb2NpYXRpbmcgd2l0aCBhbiBleGlzdGluZyBTUi0tPgo8L2JvZHk+Cgo8L2h0bWw+" data-title="init.html">
  <div class="html-preview-card" style="border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; margin: 12px 0; background: #ffffff; color: #1f2328; box-shadow: 0 2px 8px rgba(0,0,0,0.05); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <div class="html-preview-body" style="background: #ffffff; color: #1f2328; font-size: 13px; line-height: 1.5;">
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Send to Siebel</title>
  <style>
    .button-container {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }

    .custom-button {
      background-color: #2d419a;
      color: white;
      border: none;
      padding: 15px;
      border-radius: 12px;
      height: 65px;
      width: 180px;
      cursor: pointer;
      display: flex;
      justify-content: center;
      align-items: center;
      margin-right: 10px;
    }

    .custom-button:hover {
      background-color: #25aaea;
    }
  </style>
</head>

<body>
  <div class="button-container">
    <button id="new_siebel_button" class="custom-button">Add New Siebel SR</button>
    <button id="existing_siebel_button" class="custom-button">Add to Existing Siebel SR</button>
  </div>

  <!-- Add your scripts below this line -->
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.5.1/jspdf.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.2.4/jspdf.plugin.autotable.min.js"></script>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="../../AuthLibraryExtn/AuthLibraryExtn.js"></script>
  <!--This is library add-in used to fetch session and other application details-->
  <script type="text/javascript" src="logic.js"></script>
  <!--This has logic to send Incident details to Siebel for creating a New SR or associating with an existing SR-->
</body>

</html>
    </div>
  </div>
</div>

#### HTML Asset: `successMessage.html`

<div class="html-preview-pending" data-html="PCFET0NUWVBFIGh0bWw+CjxodG1sPgoKPGhlYWQ+CiAgICA8c3R5bGU+CiAgICAgICAgYm9keSB7CiAgICAgICAgICAgIG1hcmdpbjogMDsKICAgICAgICAgICAgZm9udC1mYW1pbHk6IEFyaWFsLCBzYW5zLXNlcmlmOwogICAgICAgIH0KCiAgICAgICAgYnV0dG9uIHsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogIzJkNDE5YTsKICAgICAgICAgICAgY29sb3I6IHdoaXRlOwogICAgICAgICAgICBib3JkZXI6IG5vbmU7CiAgICAgICAgICAgIHBhZGRpbmc6IDhweDsKICAgICAgICAgICAgZGlzcGxheTogYmxvY2s7CiAgICAgICAgICAgIGN1cnNvcjogcG9pbnRlcjsKICAgICAgICAgICAgbWFyZ2luLXRvcDogNXB4OwogICAgICAgICAgICBqdXN0aWZ5LWNvbnRlbnQ6IGNlbnRlcjsKICAgICAgICAgICAgYWxpZ24taXRlbXM6IGNlbnRlcjsKICAgICAgICAgICAgZm9udC1zaXplOiAxNXB4OwogICAgICAgIH0KCiAgICAgICAgYnV0dG9uOmhvdmVyIHsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogIzI1YWFlYTsKICAgICAgICB9CiAgICA8L3N0eWxlPgo8L2hlYWQ+Cgo8Ym9keT4KICAgIDxkaXY+CiAgICAgICAgPGRpdiBpZD0ic3VjY2Vzcy1tc2ciPjwvZGl2PgogICAgICAgIDxidXR0b24gaWQ9Im9rX2J0biI+T0s8L2J1dHRvbj4KICAgIDwvZGl2PgoKICAgIDxzY3JpcHQ+CiAgICAgICAgZG9jdW1lbnQuYWRkRXZlbnRMaXN0ZW5lcignRE9NQ29udGVudExvYWRlZCcsIGZ1bmN0aW9uICgpIHsKICAgICAgICAgICAgY29uc3QgcXVlcnlTdHJpbmcgPSB3aW5kb3cubG9jYXRpb24uc2VhcmNoOwogICAgICAgICAgICBjb25zdCBwYXJhbXMgPSB7fTsKICAgICAgICAgICAgcXVlcnlTdHJpbmcuc2xpY2UoMSkuc3BsaXQoJyYnKS5mb3JFYWNoKHBhcmFtID0+IHsKICAgICAgICAgICAgICAgIGNvbnN0IFtrZXksIHZhbHVlXSA9IHBhcmFtLnNwbGl0KCc9Jyk7CiAgICAgICAgICAgICAgICBwYXJhbXNba2V5XSA9IGRlY29kZVVSSUNvbXBvbmVudCh2YWx1ZSk7CiAgICAgICAgICAgIH0pOwogICAgICAgICAgICB2YXIgc2llYmVsX251bV92YWwgPSBwYXJhbXNbJ3NpZWJlbF9udW0nXTsKCiAgICAgICAgICAgIGNvbnN0IHN1Y2Nlc3NNc2cgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnc3VjY2Vzcy1tc2cnKTsKICAgICAgICAgICAgc3VjY2Vzc01zZy5pbm5lckhUTUwgPSAiU3VjY2Vzc2Z1bGx5IGFkZGVkIFNSOjxicj5TUiBOdW1iZXIocyk6IiArIHNpZWJlbF9udW1fdmFsOwogICAgICAgICAgICBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnb2tfYnRuJykuYWRkRXZlbnRMaXN0ZW5lcignY2xpY2snLAogICAgICAgICAgICAgICAgZnVuY3Rpb24gKCkgewogICAgICAgICAgICAgICAgICAgIE9SQUNMRV9TRVJWSUNFX0NMT1VELmV4dGVuc2lvbl9sb2FkZXIubG9hZCgiQ1VTVE9NX0FQUF9JRCIsICIxIikKICAgICAgICAgICAgICAgICAgICAgICAgLnRoZW4oZnVuY3Rpb24gKGV4dGVuc2lvblByb3ZpZGVyKSB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICBleHRlbnNpb25Qcm92aWRlci5yZWdpc3RlclVzZXJJbnRlcmZhY2VFeHRlbnNpb24oZnVuY3Rpb24gKElVc2VySW50ZXJmYWNlQ29udGV4dCkgewogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIElVc2VySW50ZXJmYWNlQ29udGV4dC5nZXRNb2RhbFdpbmRvd0NvbnRleHQoKS50aGVuKGZ1bmN0aW9uIChJTW9kYWxXaW5kb3dDb250ZXh0KSB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIElNb2RhbFdpbmRvd0NvbnRleHQuZ2V0Q3VycmVudE1vZGFsV2luZG93KCkudGhlbihmdW5jdGlvbiAoSU1vZGFsV2luZG93KSB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBpZiAoSU1vZGFsV2luZG93KSB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgSU1vZGFsV2luZG93LmNsb3NlKCk7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIH0pOwogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIH0pOwogICAgICAgICAgICAgICAgICAgICAgICAgICAgfSk7CiAgICAgICAgICAgICAgICAgICAgICAgIH0pOwogICAgICAgICAgICAgICAgfSk7CiAgICAgICAgfSk7CgogICAgPC9zY3JpcHQ+CjwvYm9keT4KCjwvaHRtbD4=" data-title="successMessage.html">
  <div class="html-preview-card" style="border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; margin: 12px 0; background: #ffffff; color: #1f2328; box-shadow: 0 2px 8px rgba(0,0,0,0.05); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <div class="html-preview-body" style="background: #ffffff; color: #1f2328; font-size: 13px; line-height: 1.5;">
<!DOCTYPE html>
<html>

<head>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }

        button {
            background-color: #2d419a;
            color: white;
            border: none;
            padding: 8px;
            display: block;
            cursor: pointer;
            margin-top: 5px;
            justify-content: center;
            align-items: center;
            font-size: 15px;
        }

        button:hover {
            background-color: #25aaea;
        }
    </style>
</head>

<body>
    <div>
        <div id="success-msg"></div>
        <button id="ok_btn">OK</button>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function () {
            const queryString = window.location.search;
            const params = {};
            queryString.slice(1).split('&').forEach(param => {
                const [key, value] = param.split('=');
                params[key] = decodeURIComponent(value);
            });
            var siebel_num_val = params['siebel_num'];

            const successMsg = document.getElementById('success-msg');
            successMsg.innerHTML = "Successfully added SR:<br>SR Number(s):" + siebel_num_val;
            document.getElementById('ok_btn').addEventListener('click',
                function () {
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
                });
        });

    </script>
</body>

</html>
    </div>
  </div>
</div>

#### HTML Asset: `askForSiebelNumber.html`

<div class="html-preview-pending" data-html="PCFET0NUWVBFIGh0bWw+CjxodG1sPgoKPGhlYWQ+CiAgICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9jb2RlLmpxdWVyeS5jb20vanF1ZXJ5LTMuNi4wLm1pbi5qcyI+PC9zY3JpcHQ+CiAgICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9jb2RlLmpxdWVyeS5jb20vdWkvMS4xMi4xL2pxdWVyeS11aS5qcyI+PC9zY3JpcHQ+CiAgICA8c2NyaXB0IHNyYz0iaHR0cHM6Ly9jZG5qcy5jbG91ZGZsYXJlLmNvbS9hamF4L2xpYnMvanNwZGYvMS41LjEvanNwZGYubWluLmpzIj48L3NjcmlwdD4KICAgIDxzY3JpcHQgc3JjPSJodHRwczovL2NkbmpzLmNsb3VkZmxhcmUuY29tL2FqYXgvbGlicy9qc3BkZi1hdXRvdGFibGUvMy4yLjQvanNwZGYucGx1Z2luLmF1dG90YWJsZS5taW4uanMiPjwvc2NyaXB0PgogICAgPHN0eWxlPgogICAgICAgIGJvZHkgewogICAgICAgICAgICBtYXJnaW46IDA7CiAgICAgICAgICAgIGZvbnQtZmFtaWx5OiBBcmlhbCwgc2Fucy1zZXJpZjsKICAgICAgICB9CgogICAgICAgICNhc2stc2llYmVsLW51bWJlciB7CiAgICAgICAgICAgIG1hcmdpbjogMjBweDsKICAgICAgICB9CgogICAgICAgIGxhYmVsIHsKICAgICAgICAgICAgZGlzcGxheTogYmxvY2s7CiAgICAgICAgICAgIG1hcmdpbi1ib3R0b206IDVweDsKICAgICAgICB9CgogICAgICAgIGlucHV0W3R5cGU9InRleHQiXSB7CiAgICAgICAgICAgIHdpZHRoOiAxMDAlOwogICAgICAgICAgICBwYWRkaW5nOiA4cHg7CiAgICAgICAgICAgIG1hcmdpbi1ib3R0b206IDEwcHg7CiAgICAgICAgfQoKICAgICAgICBidXR0b24gewogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjMmQ0MTlhOwogICAgICAgICAgICBjb2xvcjogd2hpdGU7CiAgICAgICAgICAgIGJvcmRlcjogbm9uZTsKICAgICAgICAgICAgcGFkZGluZzogMTBweDsKICAgICAgICAgICAgY3Vyc29yOiBwb2ludGVyOwogICAgICAgICAgICBqdXN0aWZ5LWNvbnRlbnQ6IGNlbnRlcjsKICAgICAgICAgICAgYWxpZ24taXRlbXM6IGNlbnRlcjsKICAgICAgICAgICAgbWFyZ2luLXJpZ2h0OiAxMHB4OwoKICAgICAgICB9CgogICAgICAgIGJ1dHRvbjpub3QoW2Rpc2FibGVkXSk6aG92ZXIgewogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjMjVhYWVhOwogICAgICAgIH0KCiAgICAgICAgYnV0dG9uOmRpc2FibGVkIHsKICAgICAgICAgICAgb3BhY2l0eTogMC41OwogICAgICAgICAgICBjdXJzb3I6IG5vdC1hbGxvd2VkOwogICAgICAgIH0KICAgIDwvc3R5bGU+CjwvaGVhZD4KCjxib2R5PgogICAgPGRpdiBpZD0iYXNrLXNpZWJlbC1udW1iZXIiPgogICAgICAgIDxsYWJlbCBmb3I9InNpZWJlbF9udW1iZXIiPkVudGVyIFNpZWJlbCBTUiBOdW1iZXI8L2xhYmVsPgogICAgICAgIDxpbnB1dCB0eXBlPSJ0ZXh0IiBpZD0ic2llYmVsX251bWJlciI+CiAgICAgICAgPGJ1dHRvbiBpZD0ic3VibWl0X2J0biIgZGlzYWJsZWQ+T2s8L2J1dHRvbj4KICAgICAgICA8YnV0dG9uIGlkPSJjYW5jZWxfYnRuIj5DYW5jZWw8L2J1dHRvbj4KICAgICAgICA8ZGl2IGNsYXNzPSJsb2FkZXIiIGlkPSJsb2FkZXIiIHN0eWxlPSJkaXNwbGF5OiBub25lIj48L2Rpdj4KICAgIDwvZGl2PgogICAgPHNjcmlwdCBzcmM9Ii4uLy4uL0F1dGhMaWJyYXJ5RXh0bi9BdXRoTGlicmFyeUV4dG4uanMiPjwvc2NyaXB0PgogICAgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiIHNyYz0ibG9naWMuanMiPjwvc2NyaXB0PgogICAgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiIHNyYz0iYXNrRm9yU2llYmVsTnVtYmVyLmpzIj48L3NjcmlwdD4KPC9ib2R5PgoKPC9odG1sPg==" data-title="askForSiebelNumber.html">
  <div class="html-preview-card" style="border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; margin: 12px 0; background: #ffffff; color: #1f2328; box-shadow: 0 2px 8px rgba(0,0,0,0.05); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <div class="html-preview-body" style="background: #ffffff; color: #1f2328; font-size: 13px; line-height: 1.5;">
<!DOCTYPE html>
<html>

<head>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.5.1/jspdf.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.2.4/jspdf.plugin.autotable.min.js"></script>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }

        #ask-siebel-number {
            margin: 20px;
        }

        label {
            display: block;
            margin-bottom: 5px;
        }

        input[type="text"] {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
        }

        button {
            background-color: #2d419a;
            color: white;
            border: none;
            padding: 10px;
            cursor: pointer;
            justify-content: center;
            align-items: center;
            margin-right: 10px;

        }

        button:not([disabled]):hover {
            background-color: #25aaea;
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    </style>
</head>

<body>
    <div id="ask-siebel-number">
        <label for="siebel_number">Enter Siebel SR Number</label>
        <input type="text" id="siebel_number">
        <button id="submit_btn" disabled>Ok</button>
        <button id="cancel_btn">Cancel</button>
        <div class="loader" id="loader" style="display: none"></div>
    </div>
    <script src="../../AuthLibraryExtn/AuthLibraryExtn.js"></script>
    <script type="text/javascript" src="logic.js"></script>
    <script type="text/javascript" src="askForSiebelNumber.js"></script>
</body>

</html>
    </div>
  </div>
</div>


### External Script & Library Dependencies

- **External Add-In Dependencies**: `../../AuthLibraryExtn/AuthLibraryExtn.js`
- **External Libraries (CDNs/Frameworks)**: `jquery-3.6.0.min.js`, `jquery-ui.js`, `jquery.min.js`, `jspdf.min.js`, `jspdf.plugin.autotable.min.js`

---

## OSVC Workspace Interactions

- **Fields Read**: `Incident.Created`, `Incident.IId`, `Incident.c$siebel_sr_number`
- **Fields Written**: `Incident.c$siebel_sr_number`
- **Field Listeners Registered**: `Incident.c$siebel_sr_number`
- **Workspace Lifecycle Hooks**: `RecordSaved`
- **Programmatic Editor Commands**: `Save`
- **Modal View Windows**: `askForSiebelNumber.html` (300x150px in `logic.js`), `successMessage.html?siebel_num=` (250x100px in `logic.js`)

---

## Report Dependencies & REST API Endpoints

- **Report Dependencies**: None
### API Call & Web Service Endpoints Table

| HTTP Method | Endpoint URL / Path | Operation Type | Target Object / Table | Report ID | Source Asset |
|---|---|---|---|---|---|
| `POST` | `/cc/ajaxCustom/addSrToSiebel` | `CP Controller Endpoint` | — | — | `logic.js` |

---

## Static Risk Audit Findings

| Severity | Risk Type | Detail |
|---|---|---|
| Medium | `Synchronous AJAX` | Synchronous AJAX (async: false) detected in logic.js — blocks browser UI thread |
| Medium | `Synchronous AJAX` | Synchronous AJAX (async: false) detected in askForSiebelNumber.js — blocks browser UI thread |
| **High** | `Duplicate Library Load` | Duplicate jQuery versions loaded in init.html: https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js, https://code.jquery.com/jquery-3.6.0.min.js |
| **High** | `Relative Path Dependency` | Relative path script reference '../../AuthLibraryExtn/AuthLibraryExtn.js' in init.html — will fail if add-in path changes |
| **High** | `Relative Path Dependency` | Relative path script reference '../../AuthLibraryExtn/AuthLibraryExtn.js' in askForSiebelNumber.html — will fail if add-in path changes |
| Low | `Unused Library Import` | jsPDF / jsPDF-AutoTable loaded in HTML headers but unreferenced in JavaScript |

---

## Dependency Flow Diagram

```mermaid
graph LR
  classDef addin fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;
  classDef rep fill:#a855f7,stroke:#7e22ce,stroke-width:1px,color:#fff;
  classDef api fill:#10b981,stroke:#047857,stroke-width:1px,color:#fff;
  classDef field fill:#8b5cf6,stroke:#6d28d9,stroke-width:1px,color:#fff;

  BUI_SendToSiebelBUIAddin["BUI Add-In: SendToSiebelBUIAddin"]:::addin
  API_ccajaxCustomaddSrToSiebel["API: /cc/ajaxCustom/addSrToSiebel"]:::api
  BUI_SendToSiebelBUIAddin --> |"POST"| API_ccajaxCustomaddSrToSiebel
  FW_Incidentcsiebel_sr_number["Field Write: Incident.c$siebel_sr_number"]:::field
  BUI_SendToSiebelBUIAddin -.-> |"Write"| FW_Incidentcsiebel_sr_number
```
