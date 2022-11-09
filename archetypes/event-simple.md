---
title: {{ replace .Name "-" " " | title }}
menu: side
draft: true
date: 2018-08-01
---

**When:** 01 Aug 2018
<!--more-->

The link [VeryLocal AA](/meetings/verylocal/) assumes a ``verylocal`` meeting
tag exists in ``data/meetings.yaml`` or a ``data/meetings/verylocal.yaml`` file
exists, with appropriate data.

An email (email@domain.tld) and url (https://siouxfallsaa.org) will be
automatically turned into links.

If extra content, such as a flier, is to be included with the event, then the
content type ``event`` (not ``event-simple``) is a better choice as it builds
folder where this data can be kept.

An example of a simple event is provided at ``/content/events/2022-example.md``.
