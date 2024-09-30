[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

# A Home Assistant custom component for BUTT
Home Assistant custom component for reading data and controlling a BUTT server

# BUTT

BUTT (Broadcast Using This Tool by Daniel Nöthen) is an easy to use, multi OS streaming tool.  
[More Infos](https://danielnoethen.de/butt/)

# Installation

This custom component can be installed in two different ways: `manually` or `using HACS`

## 1. Over HACS Installation

- Install [HACS - the Home Assistant Community Store](https://hacs.xyz/docs/setup/download/)
- Add this repo to HACS by:
  1. Open the HACS integrations page
  2. In the top right corner click the "Custom repositories" button
  3. Paste the url of this repository and select integration as type and add it
- Once added, restart Home Assistant
- Then go to Settings > Devices &amp; Services and click "Add Integration"
- Type "BUTT" and add the integration

## 2. Manual Installation

- Copy `custom_components/butt` folder to `<config_dir>/custom_components/butt/`
- Restart Home assistant
- Then go to Settings > Devices &amp; Services and click "Add Integration"
- Type "BUTT" and add the integration
