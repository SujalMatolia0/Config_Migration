# Custom Scripts Architecture Analysis
*Category Report: Standalone Procedural PHP / JS Scripts*

**Total Standalone Scripts Cataloged:** 260

## Overview Table

| Relative Source File Path | Script Category | Internal APIs | SOAP APIs | REST APIs | Risk Audit Flags |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `hooks.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `mapping.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `Sample.php` | `Controller Endpoint` | `0` | `0` | `0` | `[OK]` |
| `SampleLibrary.php` | `Controller Endpoint` | `0` | `0` | `0` | `[OK]` |
| `ExtendedSample.php` | `Controller Endpoint` | `0` | `0` | `0` | `[OK]` |
| `MySocialSearch.php` | `Controller Endpoint` | `0` | `0` | `0` | `[OK]` |
| `ParameterTrimSample.php` | `Model Helper` | `0` | `0` | `0` | `[OK]` |
| `Sample.php` | `Controller Endpoint` | `0` | `0` | `0` | `[OK]` |
| `answer_model.php` | `Model Helper` | `11` | `0` | `0` | `[RISK: 1]` |
| `answerfeedback_model.php` | `Model Helper` | `3` | `0` | `0` | `[OK]` |
| `clickstream_model.php` | `Model Helper` | `2` | `0` | `0` | `[OK]` |
| `contact_model.php` | `Model Helper` | `23` | `0` | `0` | `[OK]` |
| `customChat.php` | `Model Helper` | `0` | `0` | `0` | `[OK]` |
| `customfield_model.php` | `Model Helper` | `1` | `0` | `0` | `[RISK: 1]` |
| `incident_model.php` | `Model Helper` | `9` | `0` | `0` | `[RISK: 1]` |
| `report_model.php` | `Controller Endpoint` | `5` | `0` | `0` | `[RISK: 1]` |
| `sample_model.php` | `Model Helper` | `0` | `0` | `0` | `[OK]` |
| `autoload.js` | `Client-side Script` | `0` | `0` | `0` | `[OK]` |
| `error_404.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `error_exception.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `error_general.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `error_php.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `AjaxCustom.php` | `Controller Endpoint` | `0` | `0` | `0` | `[OK]` |
| `answer_full_preview.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `answer_quick_preview.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `agent.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `mobile.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `standard.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `standard_cm.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `standardchat.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `standardchat2.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `SubmitForm.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `ask.php` | `Server-side Utility` | `0` | `0` | `0` | `[RISK: 1]` |
| `ask_confirm.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `error.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `error404.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `home.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `pre_page_check.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `public_profile.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `public_profile_update.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `results.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `detail.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_landing.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_ra - Copy.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_ra.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_ra_hold.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_tac_CTO - Copy.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_tac_CTO.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_tac_login - Copy.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_tac_login.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `detail Chat.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `detail.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `intent.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `list.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `account_assistance.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `create_account.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `editing_help.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `help_search.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `login_form.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `password_changed.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `profile_updated.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `guided_assistant.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `polling_preview.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `ask.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `comment.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `overview.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `question.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `user.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `detail.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `list.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `detail Chat.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `detail.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `intent.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `list.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `ask.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `ask_confirm.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `error.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `error404.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `home.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_landing.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_landing_TAC.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_ra - Copy.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_ra.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_tac_CTO - Copy.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_tac_CTO.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_tac_login - Copy.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `chat_launch_tac_login.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `detail.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `intent.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `list.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `listold.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `account_assistance.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `create_account.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `guided_assistant.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `login_form.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `password_changed.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `profile_updated.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `post_detail.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `change_password.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `profile.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `reset_password.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `setup_password.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `detail.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `list.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `change_password.php` | `Server-side Utility` | `0` | `0` | `0` | `[RISK: 1]` |
| `overview.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `profile.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `profile_picture.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `reset_password.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `setup_password.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `list.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `unsubscribe.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `detail.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `list.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `sample.html.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `Sample.php` | `Controller Endpoint` | `0` | `0` | `0` | `[OK]` |
| `sample_helper.php` | `Server-side Utility` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic - Copy.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `viewold.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `controller.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |
| `logic.js` | `Widget Component` | `1` | `0` | `0` | `[OK]` |
| `view.php` | `Widget Component` | `0` | `0` | `0` | `[OK]` |

---

## Script Details Breakdown

### File: `hooks.php`
- **Source Relative Path**: `hooks.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `mapping.php`
- **Source Relative Path**: `mapping.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `Sample.php`
- **Source Relative Path**: `Sample.php`
- **Script Category**: `Controller Endpoint`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `SampleLibrary.php`
- **Source Relative Path**: `SampleLibrary.php`
- **Script Category**: `Controller Endpoint`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `ExtendedSample.php`
- **Source Relative Path**: `ExtendedSample.php`
- **Script Category**: `Controller Endpoint`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `MySocialSearch.php`
- **Source Relative Path**: `MySocialSearch.php`
- **Script Category**: `Controller Endpoint`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `ParameterTrimSample.php`
- **Source Relative Path**: `ParameterTrimSample.php`
- **Script Category**: `Model Helper`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `Sample.php`
- **Source Relative Path**: `Sample.php`
- **Script Category**: `Controller Endpoint`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `answer_model.php`
- **Source Relative Path**: `answer_model.php`
- **Script Category**: `Model Helper`
- **Internal APIs (ROQL/Connect)**: `11`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)

### File: `answerfeedback_model.php`
- **Source Relative Path**: `answerfeedback_model.php`
- **Script Category**: `Model Helper`
- **Internal APIs (ROQL/Connect)**: `3`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `Contact`

### File: `clickstream_model.php`
- **Source Relative Path**: `clickstream_model.php`
- **Script Category**: `Model Helper`
- **Internal APIs (ROQL/Connect)**: `2`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `contact_model.php`
- **Source Relative Path**: `contact_model.php`
- **Script Category**: `Model Helper`
- **Internal APIs (ROQL/Connect)**: `23`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `customChat.php`
- **Source Relative Path**: `customChat.php`
- **Script Category**: `Model Helper`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `customfield_model.php`
- **Source Relative Path**: `customfield_model.php`
- **Script Category**: `Model Helper`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)

### File: `incident_model.php`
- **Source Relative Path**: `incident_model.php`
- **Script Category**: `Model Helper`
- **Internal APIs (ROQL/Connect)**: `9`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)

### File: `report_model.php`
- **Source Relative Path**: `report_model.php`
- **Script Category**: `Controller Endpoint`
- **Internal APIs (ROQL/Connect)**: `5`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 5)

### File: `sample_model.php`
- **Source Relative Path**: `sample_model.php`
- **Script Category**: `Model Helper`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `autoload.js`
- **Source Relative Path**: `autoload.js`
- **Script Category**: `Client-side Script`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `error_404.php`
- **Source Relative Path**: `error_404.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `error_exception.php`
- **Source Relative Path**: `error_exception.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `error_general.php`
- **Source Relative Path**: `error_general.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `error_php.php`
- **Source Relative Path**: `error_php.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `AjaxCustom.php`
- **Source Relative Path**: `AjaxCustom.php`
- **Script Category**: `Controller Endpoint`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `answer_full_preview.php`
- **Source Relative Path**: `answer_full_preview.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **URLs / Endpoints:** `http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd`

### File: `answer_quick_preview.php`
- **Source Relative Path**: `answer_quick_preview.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **URLs / Endpoints:** `http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd`

### File: `agent.php`
- **Source Relative Path**: `agent.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **URLs / Endpoints:** `http://www.w3.org/1999/xhtml`, `http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd`

### File: `mobile.php`
- **Source Relative Path**: `mobile.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **URLs / Endpoints:** `http://schema.org/WebPage`

### File: `standard.php`
- **Source Relative Path**: `standard.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **URLs / Endpoints:** `https://dtmo.cx.defensetravel.dod.mil/ci/pta/login/redirect/answers/list/p_li/`, `https://www.defensetravel.dod.mil/neoaccess/passport.php`, `http://schema.org/WebPage`, `https://www.defensetravel.dod.mil/neoaccess/logout.php`, `https://www.defensetravel.dod.mil/neotrax/index.php`, `https://www.travel.dod.mil/`, `https://dtmo.cx.defensetravel.dod.mil/ci/pta/login/redirect/SubmitForm/p_li/`, `https://dtmo.cx.defensetravel.dod.mil/ci/pta/login/redirect/account/questions/list/p_li/`

### File: `standard_cm.php`
- **Source Relative Path**: `standard_cm.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **URLs / Endpoints:** `http://www.w3.org/1999/xhtml`, `http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd`

### File: `standardchat.php`
- **Source Relative Path**: `standardchat.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `standardchat2.php`
- **Source Relative Path**: `standardchat2.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **URLs / Endpoints:** `https://dtmo.cx.defensetravel.dod.mil/ci/pta/login/redirect/answers/list/p_li/`, `https://www.defensetravel.dod.mil/neoaccess/passport.php`, `http://schema.org/WebPage`, `https://www.defensetravel.dod.mil/neoaccess/logout.php`, `https://www.defensetravel.dod.mil`, `https://www.defensetravel.dod.mil/neotrax/index.php`, `https://dtmo.cx.defensetravel.dod.mil/ci/pta/login/redirect/SubmitForm/p_li/`, `https://dtmo.cx.defensetravel.dod.mil/ci/pta/login/redirect/account/questions/list/p_li/`

### File: `SubmitForm.php`
- **Source Relative Path**: `SubmitForm.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `ask.php`
- **Source Relative Path**: `ask.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)

### File: `ask_confirm.php`
- **Source Relative Path**: `ask_confirm.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `error.php`
- **Source Relative Path**: `error.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `error404.php`
- **Source Relative Path**: `error404.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `home.php`
- **Source Relative Path**: `home.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `pre_page_check.php`
- **Source Relative Path**: `pre_page_check.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `public_profile.php`
- **Source Relative Path**: `public_profile.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `public_profile_update.php`
- **Source Relative Path**: `public_profile_update.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `results.php`
- **Source Relative Path**: `results.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `detail.php`
- **Source Relative Path**: `detail.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_landing.php`
- **Source Relative Path**: `chat_landing.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_launch_ra - Copy.php`
- **Source Relative Path**: `chat_launch_ra - Copy.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **URLs / Endpoints:** `https://dtmo.cx.defensetravel.dod.mil/app/mobile/chat/chat_launch_ra`

### File: `chat_launch_ra.php`
- **Source Relative Path**: `chat_launch_ra.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_launch_ra_hold.php`
- **Source Relative Path**: `chat_launch_ra_hold.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **URLs / Endpoints:** `https://dtmo--tst.cx.defensetravel.dod.mil/app/mobile/chat/chat_launch_ra`

### File: `chat_launch_tac_CTO - Copy.php`
- **Source Relative Path**: `chat_launch_tac_CTO - Copy.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_launch_tac_CTO.php`
- **Source Relative Path**: `chat_launch_tac_CTO.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_launch_tac_login - Copy.php`
- **Source Relative Path**: `chat_launch_tac_login - Copy.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_launch_tac_login.php`
- **Source Relative Path**: `chat_launch_tac_login.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `detail Chat.php`
- **Source Relative Path**: `detail Chat.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `detail.php`
- **Source Relative Path**: `detail.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `intent.php`
- **Source Relative Path**: `intent.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `list.php`
- **Source Relative Path**: `list.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `account_assistance.php`
- **Source Relative Path**: `account_assistance.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `create_account.php`
- **Source Relative Path**: `create_account.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `editing_help.php`
- **Source Relative Path**: `editing_help.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `help_search.php`
- **Source Relative Path**: `help_search.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `login_form.php`
- **Source Relative Path**: `login_form.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `password_changed.php`
- **Source Relative Path**: `password_changed.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `profile_updated.php`
- **Source Relative Path**: `profile_updated.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `guided_assistant.php`
- **Source Relative Path**: `guided_assistant.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `polling_preview.php`
- **Source Relative Path**: `polling_preview.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **URLs / Endpoints:** `http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd`

### File: `ask.php`
- **Source Relative Path**: `ask.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `comment.php`
- **Source Relative Path**: `comment.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `overview.php`
- **Source Relative Path**: `overview.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `question.php`
- **Source Relative Path**: `question.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `user.php`
- **Source Relative Path**: `user.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `detail.php`
- **Source Relative Path**: `detail.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **URLs / Endpoints:** `http://schema.org/Question`

### File: `list.php`
- **Source Relative Path**: `list.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `detail Chat.php`
- **Source Relative Path**: `detail Chat.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `detail.php`
- **Source Relative Path**: `detail.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `intent.php`
- **Source Relative Path**: `intent.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `list.php`
- **Source Relative Path**: `list.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `ask.php`
- **Source Relative Path**: `ask.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `ask_confirm.php`
- **Source Relative Path**: `ask_confirm.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `error.php`
- **Source Relative Path**: `error.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `error404.php`
- **Source Relative Path**: `error404.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `home.php`
- **Source Relative Path**: `home.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_landing.php`
- **Source Relative Path**: `chat_landing.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_landing_TAC.php`
- **Source Relative Path**: `chat_landing_TAC.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_launch_ra - Copy.php`
- **Source Relative Path**: `chat_launch_ra - Copy.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_launch_ra.php`
- **Source Relative Path**: `chat_launch_ra.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_launch_tac_CTO - Copy.php`
- **Source Relative Path**: `chat_launch_tac_CTO - Copy.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_launch_tac_CTO.php`
- **Source Relative Path**: `chat_launch_tac_CTO.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_launch_tac_login - Copy.php`
- **Source Relative Path**: `chat_launch_tac_login - Copy.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `chat_launch_tac_login.php`
- **Source Relative Path**: `chat_launch_tac_login.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `detail.php`
- **Source Relative Path**: `detail.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `intent.php`
- **Source Relative Path**: `intent.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `list.php`
- **Source Relative Path**: `list.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `listold.php`
- **Source Relative Path**: `listold.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `account_assistance.php`
- **Source Relative Path**: `account_assistance.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `create_account.php`
- **Source Relative Path**: `create_account.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `guided_assistant.php`
- **Source Relative Path**: `guided_assistant.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `login_form.php`
- **Source Relative Path**: `login_form.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `password_changed.php`
- **Source Relative Path**: `password_changed.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `profile_updated.php`
- **Source Relative Path**: `profile_updated.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `post_detail.php`
- **Source Relative Path**: `post_detail.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `change_password.php`
- **Source Relative Path**: `change_password.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `profile.php`
- **Source Relative Path**: `profile.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `reset_password.php`
- **Source Relative Path**: `reset_password.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `setup_password.php`
- **Source Relative Path**: `setup_password.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `detail.php`
- **Source Relative Path**: `detail.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `list.php`
- **Source Relative Path**: `list.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `change_password.php`
- **Source Relative Path**: `change_password.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **[WARNING] Hardcoded Credential:** Potential credentials found in variable assignments (count: 1)

### File: `overview.php`
- **Source Relative Path**: `overview.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `profile.php`
- **Source Relative Path**: `profile.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `profile_picture.php`
- **Source Relative Path**: `profile_picture.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `reset_password.php`
- **Source Relative Path**: `reset_password.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `setup_password.php`
- **Source Relative Path**: `setup_password.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `list.php`
- **Source Relative Path**: `list.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `unsubscribe.php`
- **Source Relative Path**: `unsubscribe.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `detail.php`
- **Source Relative Path**: `detail.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `list.php`
- **Source Relative Path**: `list.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `sample.html.php`
- **Source Relative Path**: `sample.html.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `Sample.php`
- **Source Relative Path**: `Sample.php`
- **Script Category**: `Controller Endpoint`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `sample_helper.php`
- **Source Relative Path**: `sample_helper.php`
- **Script Category**: `Server-side Utility`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic - Copy.js`
- **Source Relative Path**: `logic - Copy.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **Imports:** `/euf/rightnow/debug-js/RightNow.Agent.js`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `viewold.php`
- **Source Relative Path**: `viewold.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `controller.php`
- **Source Relative Path**: `controller.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`

### File: `logic.js`
- **Source Relative Path**: `logic.js`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `1`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
- **OSVC Objects:** `RightNow Client Framework`

### File: `view.php`
- **Source Relative Path**: `view.php`
- **Script Category**: `Widget Component`
- **Internal APIs (ROQL/Connect)**: `0`
- **External SOAP APIs**: `0`
- **External REST APIs**: `0`
