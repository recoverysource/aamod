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

Files added to this directory can be used with a link such as
[this one](/events/2018-event-title/Flier.pdf).

If there is no need to add extra content, such as a flier, then the content type
``event-simple`` (not ``event``) is a better choice as it avoids creating an
extra directory.

An example of a simple event is provided at ``/content/events/2022-example.md``.
