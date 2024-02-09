# SMS.to for Home Assistant

This integration allows you to send SMS messages from your [Home Assistant](https://home-assistant.io/) instance.

In order to use this integration you need to create an account on [SMS.to](https://sms.to/) and get your [API_KEY](https://sms.to/app#/settings/account) from settings page.

## Install via HACS (recommended)

Go to HACS -> custom repository (upper right corner) -> enter this repository URL https://github.com/cnecrea/hass-smsto

Click on "SMS notification service through SMS.to" -> Install this repository in HACS


## Install manually

Clone or copy the repository and copy the folder custom_component/smsto' into '/custom_components'

## Configuration

Edit your home assistant configuration.yaml and add:

```yaml
notify:
  - platform: smsto
    name: SMSto
    sender: HAOS
    api_key: your_api_key
    recipient: +1XXXXXXXXXX
```
Or edit your home assistant notify.yaml and add:
```yaml
- platform: smsto
  name: SMSto
  sender: HAOS
  api_key: your_api_key
  recipient: +1XXXXXXXXXX
```

Restart home assistant

## Automations

Call service notify.smsto and enter desired message.
