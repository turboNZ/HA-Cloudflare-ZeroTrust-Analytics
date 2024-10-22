# HA-Cloudflare-ZeroTrust-Analytics
Home Assistant Custom Component to present analytic data from Cloudflare Zero Trust.

[HA-Cloudflare-ZeroTrust-Analytics](https://github.com/turboNZ/HA-Cloudflare-ZeroTrust-Analytics) is a custom component for [Home Assistant](https://www.home-assistant.io/) that allows users to ingest Analytics data directly into Home Assistant via API.

## Current Features:

 - Sensor Entity for each user tracking the following attributes:
     - Connected Application
     - IP Address
     - Connection ( Cloudflare Authentication, SSO provider information)
     - Created time
     - Ray ID
     - Country (ISO Country Code)
     - Action (E.G. Login / Logout)
   
 - Sensor displaying data from the following Cloudflare Analytics data:
     - Failed Logins
     - Accessed Applications.
  
## Configuration:
### NOTES: Currently only tested with a Global Access token from Cloudflare. Will update with correct API scopes once I've had time. This integration can also currently only be configured in YAML. 

1) Obtian your cloudflare account ID. This is displayed in the URL when logged into your Cloudflare dashboard.

2) To obtain the Global API key, go to https://dash.cloudflare.com/profile and then see API Tokens.

![Cloudflare API Key](https://github.com/turboNZ/HA-Cloudflare-ZeroTrust-Analytics/blob/main/src/images/Cloudflare-API-Key.png)

3) Add the following to your configuration (or sensors.yaml depending on how your configuration is setup). 

```
  - platform: cloudflare_analytics
    api_key: <Replace with Your API Key>
    email: <Replace with your Cloudflare Email>
    account_id: <Replace with your Cloudflare Account ID>
```

4) Restart Home Assistant.

This creates 2 sensors for showing Applications Accessed (this is currently only a counter) and the Failed logins. Additional sensors would also be created per user accessing your Zero Trust applications. 

![Home Assistant Sensors](https://github.com/turboNZ/HA-Cloudflare-ZeroTrust-Analytics/blob/main/src/images/HA-CF-Sensors.png)

The per users sensors created show data like below:

![Home Assistant Per User Sensor](https://github.com/turboNZ/HA-Cloudflare-ZeroTrust-Analytics/blob/main/src/images/HA-CF-User-Sensor.png)
